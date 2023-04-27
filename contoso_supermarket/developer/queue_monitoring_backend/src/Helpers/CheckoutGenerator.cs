namespace Contoso.Backend.Data.Helpers
{
    public class DataGenerator
    {
        private static Random random = new Random();
        private List<Checkout> checkouts;
        private List<(TimeSpan start, TimeSpan end)> peakTimes;
        private List<(TimeSpan start, TimeSpan end)> lowTrafficTimes;
        private (int min, int max) peakTimeRange;
        private (int min, int max) lowTrafficTimeRange;
        private (int min, int max) normalTimeRange;

        public DataGenerator(List<Checkout> checkouts,
            List<(TimeSpan start, TimeSpan end)> peakTimes,
            List<(TimeSpan start, TimeSpan end)> lowTrafficTimes,
            (int min, int max) lowTrafficTimeRange,
            (int min, int max) normalTimeRange,
            (int min, int max) peakTimeRange
            )
        {
            this.checkouts = checkouts;
            this.peakTimes = peakTimes;
            this.lowTrafficTimes = lowTrafficTimes;
            this.peakTimeRange = peakTimeRange;
            this.lowTrafficTimeRange = lowTrafficTimeRange;
            this.normalTimeRange = normalTimeRange;
        }

        public void GenerateCustomers(TimeSpan currentTime)
        {
            int numCustomers;
            if (IsPeakTime(currentTime))
                numCustomers = random.Next(peakTimeRange.min, peakTimeRange.max);
            else if (IsLowTrafficTime(currentTime))
                numCustomers = random.Next(lowTrafficTimeRange.min, lowTrafficTimeRange.max);
            else
                numCustomers = random.Next(normalTimeRange.min, normalTimeRange.max);

            for (int i = 0; i < numCustomers; i++)
            {
                var checkout = GetCheckoutWithShortestQueue();
                checkout.Customers.Enqueue(new Customer { CheckoutTime = checkout.AvgProcessingTime });
            }
        }

        private bool IsPeakTime(TimeSpan currentTime)
        {
            foreach (var peakTime in peakTimes)
            {
                if (peakTime.start <= peakTime.end)
                {
                    if (currentTime >= peakTime.start && currentTime <= peakTime.end)
                        return true;
                }
                else
                {
                    if (currentTime >= peakTime.start || currentTime <= peakTime.end)
                        return true;
                }
            }
            return false;
        }

        private bool IsLowTrafficTime(TimeSpan currentTime)
        {
            foreach (var lowTrafficTime in lowTrafficTimes)
            {
                if (lowTrafficTime.start <= lowTrafficTime.end)
                {
                    if (currentTime >= lowTrafficTime.start && currentTime <= lowTrafficTime.end)
                        return true;
                }
                else
                {
                    if (currentTime >= lowTrafficTime.start || currentTime <= lowTrafficTime.end)
                        return true;
                }
            }
            return false;
        }

        private Checkout GetCheckoutWithShortestQueue()
        {
            Checkout minCheckout = null;
            int minQueueLength = int.MaxValue;
            foreach (var checkout in checkouts)
                if (!checkout.Closed && checkout.Customers.Count < minQueueLength)
                {
                    minCheckout = checkout;
                    minQueueLength = checkout.Customers.Count;
                }
            return minCheckout;
        }

        public List<CheckoutHistory> GenerateData(DateTime startTime, DateTime? endTime = null, List<Checkout> updatedCheckouts = null)
        {
            if (endTime == null)
                endTime = DateTime.UtcNow;

            if (updatedCheckouts != null)
            {
                foreach (var updatedCheckout in updatedCheckouts)
                {
                    var existingCheckout = this.checkouts.FirstOrDefault(c => c.Id == updatedCheckout.Id);
                    if (existingCheckout != null)
                    {
                        existingCheckout.Type = updatedCheckout.Type;
                        existingCheckout.AvgProcessingTime = updatedCheckout.AvgProcessingTime;
                        existingCheckout.Closed = updatedCheckout.Closed;
                    }
                }
            }
            //begin at the start of the next minute
            startTime = startTime.AddMinutes(1);
            var checkoutHistories = new List<CheckoutHistory>();
            for (DateTime currentTime = startTime; currentTime <= endTime; currentTime = currentTime.AddSeconds(1))
            {
                if (currentTime.TimeOfDay.Seconds == 0)
                    GenerateCustomers(currentTime.TimeOfDay);

                foreach (var checkout in checkouts)
                {
                    if (checkout.Customers.Count > 0)
                    {
                        var customer = checkout.Customers.Peek();
                        customer.CheckoutTime -= 1;
                        if (customer.CheckoutTime <= 0)
                            checkout.Customers.Dequeue();
                    }

                    if (currentTime.TimeOfDay.Seconds == 0)
                    {
                        var checkoutHistory = new CheckoutHistory
                        {
                            Timestamp = currentTime,
                            CheckoutId = checkout.Id,
                            CheckoutType = checkout.Type,
                            QueueLength = checkout.Customers.Count,
                            AverageWaitTimeSeconds = checkout.Customers.Count * checkout.AvgProcessingTime
                        };
                        checkoutHistories.Add(checkoutHistory);
                    }
                }
            }
            return checkoutHistories;
        }
    }
}