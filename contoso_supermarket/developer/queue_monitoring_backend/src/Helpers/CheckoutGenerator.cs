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
        private int maxCustomersInStore;
        private int maxCustomersPerCheckout;

        public DataGenerator(List<Checkout> checkouts,
            List<(TimeSpan start, TimeSpan end)> peakTimes,
            List<(TimeSpan start, TimeSpan end)> lowTrafficTimes,
            (int min, int max) lowTrafficTimeRange,
            (int min, int max) normalTimeRange,
            (int min, int max) peakTimeRange,
            int maxCustomersInStore,
            int maxCustomersPerCheckout
            )
        {
            this.checkouts = checkouts;
            this.peakTimes = peakTimes;
            this.lowTrafficTimes = lowTrafficTimes;
            this.peakTimeRange = peakTimeRange;
            this.lowTrafficTimeRange = lowTrafficTimeRange;
            this.normalTimeRange = normalTimeRange;
            this.maxCustomersInStore = maxCustomersInStore;
            this.maxCustomersPerCheckout = maxCustomersPerCheckout;
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

            int totalCustomersInStore = checkouts.Sum(c => c.Customers.Count);
            numCustomers = Math.Min(numCustomers, maxCustomersInStore - totalCustomersInStore);

            for (int i = 0; i < numCustomers; i++)
            {
                var checkout = GetCheckoutWithShortestQueue();
                if (checkout.Customers.Count < maxCustomersPerCheckout)
                {
                    checkout.Customers.Enqueue(new Customer { CheckoutTime = checkout.AvgProcessingTime });
                }
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

        private Checkout GetCheckoutWithShortestQueue(int? excludedId = null)
        {
            Checkout minCheckout = null;
            int minQueueLength = int.MaxValue;
            foreach (var checkout in checkouts)
                if (!checkout.Closed && checkout.Id != excludedId && checkout.Customers.Count < minQueueLength)
                {
                    minCheckout = checkout;
                    minQueueLength = checkout.Customers.Count;
                }
            return minCheckout;
        }

        public List<CheckoutHistory> GenerateData(DateTime startTime, DateTime? endTime = null, List<Checkout> updatedCheckouts = null, bool redistributeOnly = false)
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
                        if (existingCheckout.Closed != updatedCheckout.Closed)
                        {
                            if (updatedCheckout.Closed && existingCheckout.Customers.Count > 0)
                            {
                                //redistribute customers to other open checkouts
                                while (existingCheckout.Customers.Count > 0)
                                {
                                    var checkout = GetCheckoutWithShortestQueue(existingCheckout.Id);
                                    if (checkout == null || existingCheckout.Customers.Count == 0)
                                        break;

                                    var cust = existingCheckout.Customers.Dequeue();
                                    checkout.Customers.Enqueue(cust);
                                }
                            }
                            else if (!updatedCheckout.Closed)
                            {
                                //redistribute customers to newly opened checkout
                                var totalOpenCheckouts = updatedCheckouts.Where(x => !x.Closed).Count();
                                var existingOpenCheckouts = this.checkouts.Where(c => !c.Closed).ToList();
                                int totalQueueLength = existingOpenCheckouts.Sum(c => c.Customers.Count);
                                int avgQueueLength = totalQueueLength / totalOpenCheckouts;

                                while (existingCheckout.Customers.Count < avgQueueLength)
                                {
                                    var maxQueueCheckout = existingOpenCheckouts.OrderByDescending(c => c.Customers.Count).First();
                                    if (maxQueueCheckout.Customers.Count <= avgQueueLength)
                                        break;
                                    existingCheckout.Customers.Enqueue(maxQueueCheckout.Customers.Dequeue());
                                }
                            }
                        }
                        existingCheckout.Closed = updatedCheckout.Closed;
                    }
                }
            }

            var checkoutHistories = new List<CheckoutHistory>();
            for (DateTime currentTime = startTime; currentTime <= endTime; currentTime = currentTime.AddSeconds(1))
            {
                if (currentTime.TimeOfDay.Seconds == 0 && !redistributeOnly)
                    GenerateCustomers(currentTime.TimeOfDay);

                foreach (var checkout in checkouts)
                {
                    if (checkout.Customers.Count > 0 && !redistributeOnly)
                    {
                        var customer = checkout.Customers.Peek();
                        if (customer != null)
                        {
                            customer.CheckoutTime -= 1;
                            if (customer.CheckoutTime <= 0)
                                checkout.Customers.Dequeue();
                        }
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