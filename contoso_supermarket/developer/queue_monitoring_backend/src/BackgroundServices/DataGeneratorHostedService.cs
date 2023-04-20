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

        //store constants
        private readonly List<(int CheckoutId, CheckoutType CheckoutType)> _checkoutIdAndTypes = new()
        {
            (1, CheckoutType.Express),
            (2, CheckoutType.Express),
            (3, CheckoutType.SelfService),
            (4, CheckoutType.SelfService),
            (5, CheckoutType.SelfService),
            (6, CheckoutType.SelfService),
            (7, CheckoutType.Standard),
            (8, CheckoutType.Standard)
        };
        private readonly List<(TimeSpan StartPeak, TimeSpan EndPeak)> _peakTimes = new()
        {
            (new TimeSpan(11, 30, 0), new TimeSpan(13, 0, 0)), // 11:30am - 1pm
            (new TimeSpan(17, 0, 0), new TimeSpan(18, 30, 0))   // 5pm - 6:30pm
        };
        private readonly TimeSpan _storeOpenTime = new(7, 0, 0); // 7am
        private readonly TimeSpan _storeCloseTime = new(21, 0, 0); // 9pm


        public TimedHostedService(ILogger<TimedHostedService> logger, PostgreSqlService postgreSqlService, IConfiguration configuration)
        {
            _logger = logger;
            _postgreSqlService = postgreSqlService;
            _timeZone = configuration["timeZone"];
        }

        public async Task StartAsync(CancellationToken stoppingToken)
        {
            _logger.LogInformation("Timed Hosted Service running.");

            //if database empty then back fill a day till now
            var checkoutHistoryPopulated = await _postgreSqlService.TableHasValue("contoso.checkout_history");
            if (!checkoutHistoryPopulated)
            {
                var endDate = DateTimeOffset.UtcNow.ConvertTimeZone(_timeZone);
                var startDate = new DateTimeOffset(endDate.Date.AddDays(-1)).AppendTimeZone(_timeZone);
                var checkoutData = CheckoutGenerator.GenerateCheckoutData(_checkoutIdAndTypes, _peakTimes, startDate, endDate, _storeOpenTime, _storeCloseTime);
                await _postgreSqlService.BulkUpsertCheckoutHistory(checkoutData);
            }

            //starting timer
            _timer = new Timer(DoWork, null, TimeSpan.Zero, TimeSpan.FromSeconds(60));
        }

        private void DoWork(object? state)
        {

            var startDate = (_postgreSqlService.GetMaxCheckoutHistoryTimestamp().Result).ConvertTimeZone(_timeZone);
            var endDate = DateTimeOffset.UtcNow.ConvertTimeZone(_timeZone);
            _logger.LogInformation($"Generating data between {startDate}-{endDate}...");

            var checkoutData = CheckoutGenerator.GenerateCheckoutData(_checkoutIdAndTypes, _peakTimes, startDate, endDate, _storeOpenTime, _storeCloseTime);
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
