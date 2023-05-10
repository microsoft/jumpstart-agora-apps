using Contoso.Backend.Data.Helpers;
using Contoso.Backend.Data.Services;

namespace Contoso.Backend.Data.BackgroundServices
{
    public class TimedHostedService : IHostedService, IDisposable
    {
        private readonly ILogger<TimedHostedService> _logger;
        private readonly PostgreSqlService _postgreSqlService;
        private Timer? _timer = null;
        private readonly DataGenerator _checkoutDataGenerator;

        // Maximum number of days to keep checkout history data in the database
        private readonly int MAX_DAYS_OF_CHECKOUT_HISTORY = 2;

        // Peak times for store traffic
        private readonly List<(TimeSpan start, TimeSpan end)> _peakTimes = new List<(TimeSpan start, TimeSpan end)>
        {
            (new TimeSpan(12, 0, 0), new TimeSpan(13, 0, 0)),
            (new TimeSpan(17, 0, 0), new TimeSpan(19, 0, 0))
        };

        // Low traffic times for store traffic
        private readonly List<(TimeSpan start, TimeSpan end)> _lowTrafficTimes = new List<(TimeSpan start, TimeSpan end)>
        {
             (new TimeSpan(22, 0, 0), new TimeSpan(7, 0, 0))
        };

        public TimedHostedService(ILogger<TimedHostedService> logger, PostgreSqlService postgreSqlService, IConfiguration configuration)
        {
            _logger = logger;
            _postgreSqlService = postgreSqlService;
            var checkouts = _postgreSqlService.GetCheckouts().Result;

            // Initialize the data generator with checkout data and store traffic information
            _checkoutDataGenerator = new DataGenerator(checkouts, _peakTimes, _lowTrafficTimes, (0, 5), (4, 15), (8, 12), 200, 10);
        }

        public async Task StartAsync(CancellationToken stoppingToken)
        {
            _logger.LogInformation("Timed Hosted Service running.");

            // Check if the checkout history table has any data
            var checkoutHistoryPopulated = await _postgreSqlService.TableHasValue("contoso.checkout_history");
            if (!checkoutHistoryPopulated)
            {
                // If the table is empty, backfill data for the past 2 days
                var startDate = DateTime.UtcNow.AddDays(-2);
                var checkouts = await _postgreSqlService.GetCheckouts();
                var checkoutData =
                    _checkoutDataGenerator.GenerateData(startDate, null, checkouts);
                await _postgreSqlService.BulkUpsertCheckoutHistory(checkoutData);
            }
            else
            {
                // Clear out any data that is older than the maximum number of days specified
                await _postgreSqlService.DeleteOldCheckoutHistory(MAX_DAYS_OF_CHECKOUT_HISTORY);
            }

            // Start the timer to periodically generate and update data
            _timer = new Timer(DoWork, null, TimeSpan.Zero,
                TimeSpan.FromSeconds(60));
        }

        private void DoWork(object? state)
        {
            // Get the maximum timestamp from the checkout history table
            var startDate = _postgreSqlService.GetMaxCheckoutHistoryTimestamp().Result;
            var endDate = DateTime.UtcNow;
            _logger.LogInformation($"Generating data between {startDate}-{endDate}...");
            var checkouts = _postgreSqlService.GetCheckouts().Result;

            // Generate new checkout history data
            var checkoutData = _checkoutDataGenerator.GenerateData(startDate.UtcDateTime, endDate, checkouts);

            // Update the database with the new data
            _postgreSqlService.BulkUpsertCheckoutHistory(checkoutData).Wait();

            // Clear out any data that is older than the maximum number of days specified
            _postgreSqlService.DeleteOldCheckoutHistory(MAX_DAYS_OF_CHECKOUT_HISTORY).Wait();
        }

        public void RedistributeQueues()
        {
            // Redistributes the queues by regenerating data
            var startDate = _postgreSqlService.GetMaxCheckoutHistoryTimestamp().Result;
            var endDate = DateTime.UtcNow;
            var checkouts = _postgreSqlService.GetCheckouts().Result;

            // Generate new checkout history data with queue redistribution
            var checkoutData =
                _checkoutDataGenerator.GenerateData(startDate.UtcDateTime,
                    endDate,
                    checkouts,
                    true);

            // Update the database with the new data
            _postgreSqlService.BulkUpsertCheckoutHistory(checkoutData).Wait();
        }

        public Task StopAsync(CancellationToken stoppingToken)
        {
            // Stop the timer when the service is stopping
            _logger.LogInformation("Timed Hosted Service is stopping.");
            _timer?.Change(Timeout.Infinite, 0);
            return Task.CompletedTask;
        }

        public void Dispose() => _timer?.Dispose();
    }
}