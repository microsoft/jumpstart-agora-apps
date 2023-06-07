// See https://aka.ms/new-console-template for more information
using DataEmulator;
using Microsoft.Azure.Cosmos;
using Azure.Identity;
using Azure.ResourceManager;
using Azure.ResourceManager.CosmosDB;
using Azure.ResourceManager.CosmosDB.Models;
using System.Configuration;
using System.Text.RegularExpressions;
using System.Text.Json;
using System.Text.Json.Serialization;

Console.WriteLine("Please confirm if you wish to generate sample data! Yes (Y) or No (N): ");
string? confirm = Console.ReadLine();
if (string.IsNullOrEmpty(confirm))
{
    Console.WriteLine("Exiting application.");
    Environment.Exit(0);
}

if (!Regex.IsMatch(confirm, "(?i)^[y|yes]$"))
{
    Console.WriteLine("Existing application.");
    Environment.Exit(0);
}


// Get configuration values from environment variables. These environment variables are setup as part of Agora deployment.
var cosmosAccountName = Environment.GetEnvironmentVariable("cosmosDBName", EnvironmentVariableTarget.Machine);
var spnTenantId = Environment.GetEnvironmentVariable("SPN_TENANT_ID", EnvironmentVariableTarget.Machine);
var spnClientId = Environment.GetEnvironmentVariable("SPN_CLIENT_ID", EnvironmentVariableTarget.Machine);
var spnClientSecret = Environment.GetEnvironmentVariable("SPN_CLIENT_SECRET", EnvironmentVariableTarget.Machine);
var subscriptionId = Environment.GetEnvironmentVariable("subscriptionId", EnvironmentVariableTarget.Machine);
var resourceGroup = Environment.GetEnvironmentVariable("resourceGroup", EnvironmentVariableTarget.Machine);
var cosmosDatabaseName = Environment.GetEnvironmentVariable("cosmosDatabaseName", EnvironmentVariableTarget.Machine);
var containerName = Environment.GetEnvironmentVariable("containerName", EnvironmentVariableTarget.Machine);
int NoOfDays = -30;

// Use App.Config when running outside of Agora client VM. Configure these values in App.Config to generate test data.
if (String.IsNullOrEmpty(cosmosAccountName)){ cosmosAccountName = ConfigurationManager.AppSettings["cosmosDBName"]; }
if (String.IsNullOrEmpty(spnTenantId)) { spnTenantId = ConfigurationManager.AppSettings["SPN_TENANT_ID"]; }
if (String.IsNullOrEmpty(spnClientId)) { spnClientId = ConfigurationManager.AppSettings["SPN_CLIENT_ID"]; }
if (String.IsNullOrEmpty(spnClientSecret)) { spnClientSecret = ConfigurationManager.AppSettings["SPN_CLIENT_SECRET"]; }
if (String.IsNullOrEmpty(subscriptionId)) { subscriptionId = ConfigurationManager.AppSettings["subscriptionId"]; }
if (String.IsNullOrEmpty(resourceGroup)) { resourceGroup = ConfigurationManager.AppSettings["resourceGroup"]; }
if (String.IsNullOrEmpty(cosmosDatabaseName)) { cosmosDatabaseName = ConfigurationManager.AppSettings["cosmosDatabaseName"]; } else { cosmosDatabaseName = "Orders"; }
if (String.IsNullOrEmpty(containerName)) { containerName = ConfigurationManager.AppSettings["containerName"]; } else { cosmosDatabaseName = "Orders"; }

string history = ConfigurationManager.AppSettings["NoOfDays"] ?? "-30";
if (string.IsNullOrEmpty(history))
{
    NoOfDays = int.Parse(history);
}

Console.WriteLine("cosmosDBName: {0}", cosmosAccountName);
Console.WriteLine("SPN_TENANT_ID: {0}", spnTenantId);
Console.WriteLine("SPN_CLIENT_ID: {0}", spnClientId);
Console.WriteLine("subscriptionId: {0}", subscriptionId);
Console.WriteLine("resourceGroup: {0}", resourceGroup);
Console.WriteLine("cosmosDatabaseName: {0}", cosmosDatabaseName);
Console.WriteLine("containerName: {0}", containerName);
Console.WriteLine("No of days to generate history: {0}", NoOfDays);

// Assign defaults if not configured
if (String.IsNullOrEmpty(cosmosDatabaseName)) { cosmosDatabaseName = "Orders"; }
if (String.IsNullOrEmpty(containerName)) { containerName = "Orders"; }

CosmosClient? cosmosClient = null;

if (!String.IsNullOrEmpty(cosmosAccountName))
{
    // Get CosmosDB connection string using Azure Resource Manager APIs
    Console.WriteLine("Retrieving CosmosDB connection string using Azure Resource Manager in the current subscription.");
    ClientSecretCredential clientCreds = new ClientSecretCredential(spnTenantId, spnClientId, spnClientSecret);
    ArmClient armClient = new ArmClient(clientCreds, subscriptionId);

    CosmosDBAccountResource cosmosDBAccount = armClient.GetCosmosDBAccountResource(CosmosDBAccountResource.CreateResourceIdentifier(subscriptionId, resourceGroup, cosmosAccountName));
    CosmosDBAccountConnectionString connectionString = cosmosDBAccount.GetConnectionStrings().First<CosmosDBAccountConnectionString>();
    if (connectionString != null)
    {
        Console.WriteLine("Retrieved CosmosDB connection string from the CosmosDB account.");
        cosmosClient = new CosmosClient(connectionString.ConnectionString);
    }
    else
    {
        Console.WriteLine("Could not retrieve CosmosDB connection string using Azure Resource Manager in the current subscription.");
        System.Environment.Exit(-1);
    }
}

// Create product and store list simulate data
List<Product> productList = new List<Product>();
List<Store> storeList = new List<Store>();

try
{
    // Get databae
    if (null == cosmosClient)
    {
        Console.WriteLine("Could not create CosmosDB client.");
        System.Environment.Exit(-1);
    }

    Database cosmosDB = cosmosClient.GetDatabase(cosmosDatabaseName);
    if (null == cosmosDB)
    {
        // Create new database
        Console.WriteLine("Database not found in the CosmosDB account. Creating new database.");
        cosmosDB = await cosmosClient.CreateDatabaseAsync(id: cosmosDatabaseName);
        if (null == cosmosDB)
        {
            Console.WriteLine("Could not create CosmosDB database.");
            System.Environment.Exit(-1);
        }
    }
    
    // Get or Create Orders container
    Container ordersContainer = await cosmosDB.CreateContainerIfNotExistsAsync(id: containerName, partitionKeyPath: "/OrderId");
    if (null == ordersContainer)
    {
        Console.WriteLine("Could not create CosmosDB container.");
        System.Environment.Exit(-1);
    }

    // Read products list from Products container to generate orders
    Console.WriteLine("Retrieving product information from Products container.");
    Container productsContainer = cosmosDB.GetContainer("Products");
    if(productsContainer != null)
    {
        using FeedIterator<Product> productIterator = productsContainer.GetItemQueryIterator<Product>(queryText: "SELECT * FROM Products");
        if (productIterator.HasMoreResults)
        {
            try
            {
                foreach (Product product in await productIterator.ReadNextAsync())
                {
                    productList.Add(product);
                }
            }
            catch(Exception)
            {
                // Skip if could not find any items in Products container
            }
        }
    }

    // If Products container is not populated, generate new Products using below info or JSON file
    if (productList.Count <= 0)
    {
        // Import products from JSON file
        string productsJsonFile = string.Format(@"{0}\{1}", AppContext.BaseDirectory, ConfigurationManager.AppSettings["productsJsonFile"]);
        if (System.IO.File.Exists(productsJsonFile))
        {
            string productsJson = System.IO.File.ReadAllText(productsJsonFile);
            if (!string.IsNullOrEmpty(productsJson))
            {
                productList = JsonSerializer.Deserialize<List<Product>>(productsJson);
            }
        }
        else
        {
            Console.WriteLine("No products available to generate sample data. Upload products information into Products container in CosmosDB.");
            System.Environment.Exit(-1);
        }
    }
    else
    {
        Console.WriteLine("Found {0} products in the container to generate sample data.", productList.Count);
    }

    // Get Store list to generate random orders from these stores
    Console.WriteLine("Retrieving stores information from Stores container.");
    Container storesContainer = cosmosDB.GetContainer("Stores");
    if (storesContainer != null )
    {
        using FeedIterator<Store> storeIterator = storesContainer.GetItemQueryIterator<Store>(queryText: "SELECT * FROM Stores");
        try
        {
            foreach (Store Store in await storeIterator.ReadNextAsync())
            {
                storeList.Add(Store);
            }
        }
        catch (Exception)
        {
            // Skip if could not find any items in Stores container
        }
    }
    
    // Create new Stores list if no stores exist in the Stores container
    if (storeList.Count <= 0)
    {
        // Import products from JSON file
        string storesJsonFile = string.Format(@"{0}\{1}", AppContext.BaseDirectory, ConfigurationManager.AppSettings["storesJsonFile"]);
        if (System.IO.File.Exists(storesJsonFile))
        {
            string storesJson = System.IO.File.ReadAllText(storesJsonFile);
            if (!string.IsNullOrEmpty(storesJson))
            {
                storeList = JsonSerializer.Deserialize<List<Store>>(storesJson);
            }
        }
        else
        {
            Console.WriteLine("No stores information available to generate sample data. Upload stores information into Stores container in CosmosDB.");
            System.Environment.Exit(-1);
        }
    }
    else
    {
        Console.WriteLine("Found {0} stores in the container to generate sample data.", storeList.Count);
    }

    DateTime dataStartDate = DateTime.Now.AddDays(NoOfDays);
    Random random = new Random();
    Product[] products = productList.ToArray<Product>();
    Store[] stores = storeList.ToArray();

    do
    {
        Console.WriteLine("Generate sample data for: {0}", dataStartDate.ToString("MMM/dd/yyyy"));

        // Create random order count based on the time of the day and day of the week
        int randomOrders = 0;
        switch (dataStartDate.DayOfWeek)
        {
            case DayOfWeek.Saturday:
            case DayOfWeek.Sunday:
                if (dataStartDate.Hour > 8 && dataStartDate.Hour < 20){
                    randomOrders = random.Next(20, 50);
                }
                else if (dataStartDate.Hour > 6 && dataStartDate.Hour < 22)
                {
                    randomOrders = random.Next(10, 20);
                }
                else
                {
                    randomOrders = random.Next(0, 5);
                }
                break;
             default:
                if (dataStartDate.Hour > 8 && dataStartDate.Hour < 20)
                {
                    randomOrders = random.Next(10, 30);
                }
                else if (dataStartDate.Hour > 6 && dataStartDate.Hour < 22)
                {
                    randomOrders = random.Next(5, 10);
                }
                else
                {
                    randomOrders = random.Next(0, 5);
                }
                break;
        }
            

        // Generate orders
        for(int orderNo = 1; orderNo <= randomOrders; orderNo++)
        {
            // Select random store
            var storeIndex= random.Next(0, stores.Length-1);
            var order = new Order();
            order.storeId = stores[storeIndex].id.ToString();

            order.orderDate = dataStartDate;
            order.id = string.Format("{0}{1:D2}", dataStartDate.ToString("yyyMMddHHmmss"), orderNo);
            order.cloudSynced = true;

            // Generate random number of items
            var randomOrderItems = random.Next(1, products.Length);

            // Pick random items from product list
            var randomProductIndexList = new List<int>();
            while (randomProductIndexList.Count < randomOrderItems)
            {
                int productIndex = random.Next(0, products.Length-1);
                if (!randomProductIndexList.Contains(productIndex)) randomProductIndexList.Add(productIndex);
            }

            // Add items to the order
            List<orderdetails> orderitems = new List<orderdetails>();
            int itemIndex = 0;
            foreach (var productIndex in randomProductIndexList)
            {
                orderdetails item = new orderdetails() { id = ++itemIndex, name = products[productIndex].name, price = products[productIndex].price, quantity = random.Next(1, 10) };
                orderitems.Add(item);
            }

            order.orderdetails = orderitems.ToArray();

            // Write into CosmosDB
            try
            {
                var createdProdct = await ordersContainer.CreateItemAsync<Order>(item: order);
                if (null == createdProdct)
                {
                    // At this point, the batch is full but our last event was not
                    // accepted.  For our purposes, the event is unimportant so we
                    // will intentionally ignore it.  In a real-world scenario, a
                    // decision would have to be made as to whether the event should
                    // be dropped or published on its own.

                    break;
                }
            }
            catch(CosmosException exp) {
                Console.WriteLine(exp.Message);
            }
        }

        // Increase time until it reaches current time
        dataStartDate = dataStartDate.AddMinutes(random.Next(10, 50));

    } while (dataStartDate < DateTime.Now);

    Console.WriteLine("Finished generating sample data and ready to view in Azure Data Explorer dashboards. Please give some time to synchronize in Azure Data Exlorer before viewing dashboards.");
}
catch (Exception ex)
{ 
    Console.WriteLine("Failed to generate sample data.");
    Console.WriteLine(ex.ToString());
}
finally
{
    // Close CosmosDB connection gracefully
    if (null != cosmosClient)
    {
        cosmosClient.Dispose();
    }
}
