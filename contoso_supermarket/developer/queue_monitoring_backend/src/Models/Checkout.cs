using System.Text.Json.Serialization;

public class Checkout
{
    public int Id { get; set; }
    public CheckoutType Type { get; set; }
    public int AvgProcessingTime { get; set; }

    public bool Closed { get; set; }
    [JsonIgnore]
    public Queue<Customer> Customers { get; set; }

    public Checkout(int id, CheckoutType type, int avgProcessingTime, bool closed = false)
    {
        Id = id;
        Type = type;
        AvgProcessingTime = avgProcessingTime;
        Customers = new Queue<Customer>();
        Closed = closed;
    }
}