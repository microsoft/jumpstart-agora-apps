using System.Globalization;

namespace Contoso.Backend.Data.Helpers
{
    public static class CheckoutGenerator
    {
        public static List<CheckoutHistory> GenerateCheckoutData(
          List<(int CheckoutId, CheckoutType CheckoutType)> checkoutIdAndTypes,
          List<(TimeSpan StartPeak, TimeSpan EndPeak)> peakTimes,
          DateTimeOffset startDate,
          DateTimeOffset endDate,
          TimeSpan storeOpenTime,
          TimeSpan storeCloseTime,
          int baseQueueLength = 5,
          double expressMultiplier = 0.5,
          double selfServiceMultiplier = 0.7,
          double standardQueueTime = 60,
          double peakMultiplier = 1.5,
          double offPeakMultiplier = 1.0,
          double peakQueueMultiplier = 1.5
          )
        {
            var checkoutData = new List<CheckoutHistory>();

            // Iterate over the date range
            var currentDate = startDate.AddMinutes(1);
            while (currentDate < endDate)
            {
                // Check if store is open
                if (currentDate.TimeOfDay >= storeOpenTime && currentDate.TimeOfDay < storeCloseTime)
                {
                    // Determine if the current time is within a peak period
                    var isPeakTime = false;
                    foreach (var peakTime in peakTimes)
                    {
                        var startTime = currentDate.Date + peakTime.StartPeak;
                        var endTime = currentDate.Date + peakTime.EndPeak;
                        if (currentDate.DateTime >= startTime && currentDate.DateTime < endTime)
                        {
                            isPeakTime = true;
                            break;
                        }
                    }

                    // Iterate over the checkout IDs and types
                    foreach (var checkoutIdAndType in checkoutIdAndTypes)
                    {
                        // Determine the queue length based on the current time and checkout type
                        var queueLength = 0;
                        if (isPeakTime)
                        {
                            queueLength = baseQueueLength + new Random().Next((int)(baseQueueLength * peakQueueMultiplier));
                        }
                        else
                        {
                            queueLength = new Random().Next(baseQueueLength);
                        }

                        // Determine the processing time based on the checkout type
                        double processingTimeSeconds;
                        switch (checkoutIdAndType.CheckoutType)
                        {
                            case CheckoutType.Express:
                                processingTimeSeconds = expressMultiplier * standardQueueTime;
                                break;
                            case CheckoutType.SelfService:
                                processingTimeSeconds = selfServiceMultiplier * standardQueueTime;
                                break;
                            case CheckoutType.Standard:
                            default:
                                processingTimeSeconds = standardQueueTime;
                                break;
                        }

                        // Determine the wait time based on the current queue length
                        var waitTimeSeconds = processingTimeSeconds * queueLength;
                        if (isPeakTime)
                        {
                            waitTimeSeconds *= peakMultiplier;
                        }
                        else
                        {
                            waitTimeSeconds *= offPeakMultiplier;
                        }

                        // Add the checkout state to the list
                        checkoutData.Add(new CheckoutHistory
                        {
                            Timestamp = currentDate.UtcDateTime,
                            CheckoutId = checkoutIdAndType.CheckoutId,
                            CheckoutType = checkoutIdAndType.CheckoutType,
                            QueueLength = queueLength,
                            AverageWaitTimeSeconds = waitTimeSeconds
                        });
                    }
                }
                // Move to the next minute
                currentDate = currentDate.AddMinutes(1);
            }

            return checkoutData;
        }

        public static void WriteCheckoutDataToCsv(List<CheckoutHistory> checkoutData, string filePath)
        {
            using (var writer = new StreamWriter(filePath))
            {
                writer.WriteLine($"{nameof(CheckoutHistory.Timestamp)},{nameof(CheckoutHistory.CheckoutId)},{nameof(CheckoutHistory.CheckoutType)},{nameof(CheckoutHistory.QueueLength)},{nameof(CheckoutHistory.AverageWaitTimeSeconds)}");

                foreach (var checkoutState in checkoutData)
                {
                    var timestamp = checkoutState.Timestamp.ToString("yyyy-MM-ddTHH:mm:sszzz", CultureInfo.InvariantCulture);
                    var checkoutId = checkoutState.CheckoutId;
                    var checkoutType = checkoutState.CheckoutType.ToString();
                    var queueLength = checkoutState.QueueLength.ToString();
                    var averageWaitTimeSeconds = checkoutState.AverageWaitTimeSeconds.ToString(CultureInfo.InvariantCulture);

                    writer.WriteLine($"{timestamp},{checkoutId},{checkoutType},{queueLength},{averageWaitTimeSeconds}");
                }
            }
        }
    }
}