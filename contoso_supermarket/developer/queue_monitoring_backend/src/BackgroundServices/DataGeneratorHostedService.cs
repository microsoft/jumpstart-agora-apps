using Contoso.Backend.Data.Helpers;
using Contoso.Backend.Data.Services;

namespace Contoso.Backend.Data.BackgroundServices
{
    public class TimedHostedService : IHostedService, IDisposable
    {
        private readonly ILogger<TimedHostedService> _logger;
        private readonly PostgreSqlService _postgreSqlService;
        private readonly string? _timeZone;
        private Timer? _timer = null;

        private readonly DataGenerator _checkoutDataGenerator;

        //store constants
        private readonly List<(TimeSpan start, TimeSpan end)> _peakTimes = new List<(TimeSpan start, TimeSpan end)>
        {
            (new TimeSpan(12, 0, 0), new TimeSpan(13, 0, 0)),
            (new TimeSpan(17, 0, 0), new TimeSpan(19, 0, 0))
        };

        private readonly List<(TimeSpan start, TimeSpan end)> _lowTrafficTimes = new List<(TimeSpan start, TimeSpan end)>
        {
             (new TimeSpan(22, 0, 0), new TimeSpan(7, 0, 0))
        };

        public TimedHostedService(ILogger<TimedHostedService> logger, PostgreSqlService postgreSqlService, IConfiguration configuration)
        {
            _logger = logger;
            _postgreSqlService = postgreSqlService;
            _timeZone = configuration["TIMEZONE"];
            var checkouts = _postgreSqlService.GetCheckouts().Result;

            _checkoutDataGenerator = new DataGenerator(checkouts, _peakTimes, _lowTrafficTimes, (0, 5), (0, 15), (8, 20));
        }

        public async Task StartAsync(CancellationToken stoppingToken)
        {
            _logger.LogInformation("Timed Hosted Service running.");

            //if database empty then back fill a day till now
            var checkoutHistoryPopulated = await _postgreSqlService.TableHasValue("contoso.checkout_history");
            if (!checkoutHistoryPopulated)
            {
                // var endDate = DateTimeOffset.UtcNow.ConvertTimeZone(_timeZone);
                var startDate = DateTime.UtcNow.AddDays(-1);
                var checkouts = await _postgreSqlService.GetCheckouts();
                var checkoutData = _checkoutDataGenerator.GenerateData(startDate, null, checkouts);
                await _postgreSqlService.BulkUpsertCheckoutHistory(checkoutData);
            }

            //starting timer
            _timer = new Timer(DoWork, null, TimeSpan.Zero, TimeSpan.FromSeconds(60));
        }

        private void DoWork(object? state) 
        {

            var startDate = _postgreSqlService.GetMaxCheckoutHistoryTimestamp().Result;
            var endDate = DateTime.UtcNow;
            _logger.LogInformation($"Generating data between {startDate}-{endDate}...");
            var checkouts = _postgreSqlService.GetCheckouts().Result;
            var checkoutData = _checkoutDataGenerator.GenerateData(startDate.UtcDateTime, endDate, checkouts);
            _postgreSqlService.BulkUpsertCheckoutHistory(checkoutData).Wait();
        }

        public Task StopAsync(CancellationToken stoppingToken)
        {
            _logger.LogInformation("Timed Hosted Service is stopping.");
            _timer?.Change(Timeout.Infinite, 0);
            return Task.CompletedTask;
        }

        public void Dispose() => _timer?.Dispose();
    }
}
