using Contoso.Backend.Data.BackgroundServices;
using Contoso.Backend.Data.Services;

var builder = WebApplication.CreateBuilder(args);
var Configuration = builder.Configuration;

// Add services to the container.
// Learn more about configuring Swagger/OpenAPI at https://aka.ms/aspnetcore/swashbuckle
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();
builder.Services.AddSingleton(new PostgreSqlService($"Host={Configuration["SQL_HOST"]};Username={Configuration["SQL_USERNAME"]};Password={Configuration["SQL_PASSWORD"]};Database={Configuration["SQL_DATABASE"]}"));
builder.Services.AddHostedService<TimedHostedService>();

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();

app.MapGet("api/checkoutHistory", async (PostgreSqlService postgreSqlService, DateTimeOffset? startDate, DateTimeOffset? endDate) =>
{
    List<CheckoutHistory> checkoutHistory = await postgreSqlService.GetCheckoutHistory(startDate, endDate);
    return checkoutHistory;
})
.WithName("GetCheckoutHistory")
.WithOpenApi();

app.MapGet("api/products", async (PostgreSqlService postgreSqlService) =>
{
    List<Product> products = await postgreSqlService.GetProducts();
    return products;
})
.WithName("GetProducts")
.WithOpenApi();

app.MapPost("api/products", async (PostgreSqlService postgreSqlService, List<Product> products) =>
{
    await postgreSqlService.UpdateProducts(products);
})
.WithName("UpdateProducts")
.WithOpenApi();

app.Run();