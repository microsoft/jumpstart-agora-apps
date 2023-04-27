public enum CheckoutType
{
    Standard = 1,
    Express = 2,
    SelfService = 3
}

public class CheckoutHistory
{
    public DateTimeOffset Timestamp { get; set; }
    public int CheckoutId { get; set; }
    public CheckoutType CheckoutType { get; set; }
    public int QueueLength { get; set; }
    public double AverageWaitTimeSeconds { get; set; }
}