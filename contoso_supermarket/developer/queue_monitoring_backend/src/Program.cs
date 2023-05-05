using Contoso.Backend.Data.BackgroundServices;
using Contoso.Backend.Data.Services;
using Microsoft.AspNetCore.Mvc;

var builder = WebApplication.CreateBuilder(args);
var Configuration = builder.Configuration;

// Add services to the container.
// Learn more about configuring Swagger/OpenAPI at https://aka.ms/aspnetcore/swashbuckle
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();
builder.Services.AddSingleton<PostgreSqlService>(serviceProvider =>
{
    var configuration = serviceProvider.GetRequiredService<IConfiguration>();
    var logger = serviceProvider.GetRequiredService<ILogger<PostgreSqlService>>();
    var connectionString = $"Host={configuration["SQL_HOST"]};Username={configuration["SQL_USERNAME"]};Password={configuration["SQL_PASSWORD"]};Database={configuration["SQL_DATABASE"]}";
    return new PostgreSqlService(logger, connectionString);
});
builder.Services.AddSingleton<TimedHostedService>();
builder.Services.AddHostedService<TimedHostedService>(provider => provider.GetService<TimedHostedService>());

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
    await postgreSqlService.UpsertProducts(products);
})
.WithName("UpdateProducts")
.WithOpenApi();

app.MapDelete("api/products/{productId}", async (PostgreSqlService postgreSqlService, int productId) =>
{
    await postgreSqlService.DeleteProduct(productId);
})
.WithName("DeleteProduct")
.WithOpenApi();

app.MapGet("api/checkouts/", async (PostgreSqlService postgreSqlService) =>
{
    return await postgreSqlService.GetCheckouts();
})
.WithName("GetCheckouts")
.WithOpenApi();

app.MapGet("api/checkouts/{checkoutId}/toggle", async ([FromServices] PostgreSqlService postgreSqlService, [FromServices] TimedHostedService ths, int checkoutId) =>
{
    var toggleCheckout = await postgreSqlService.ToggleCheckout(checkoutId);
    ths.RedistributeQueues();
    return toggleCheckout;
})
.WithName("ToggleCheckout")
.WithOpenApi();

app.Run();