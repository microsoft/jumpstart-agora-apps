// See https://aka.ms/new-console-template for more information
using DataEmulator;
using Microsoft.Azure.Cosmos;
using Azure.Identity;
using Azure.ResourceManager;
using Azure.ResourceManager.CosmosDB;
using Azure.ResourceManager.CosmosDB.Models;
using System.Configuration;
using System.Text.Json;
using System.Text.Json.Serialization;
using Newtonsoft.Json;

if (args?.Length > 0)
{
    foreach (string arg in args)
    {
        Console.WriteLine(arg);
    }
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
var productsJsonFile = Environment.GetEnvironmentVariable("productsJsonFile", EnvironmentVariableTarget.Machine);
var storesJsonFile = Environment.GetEnvironmentVariable("storesJsonFile", EnvironmentVariableTarget.Machine);
int NoOfDays = -30;

// Use App.Config when running outside of Agora client VM. Configure thes values in App.Config to generate test data.
if (String.IsNullOrEmpty(cosmosAccountName)){ cosmosAccountName = ConfigurationManager.AppSettings["cosmosDBName"]; }
if (String.IsNullOrEmpty(spnTenantId)) { spnTenantId = ConfigurationManager.AppSettings["SPN_TENANT_ID"]; }
if (String.IsNullOrEmpty(spnClientId)) { spnClientId = ConfigurationManager.AppSettings["SPN_CLIENT_ID"]; }
if (String.IsNullOrEmpty(spnClientSecret)) { spnClientSecret = ConfigurationManager.AppSettings["SPN_CLIENT_SECRET"]; }
if (String.IsNullOrEmpty(subscriptionId)) { subscriptionId = ConfigurationManager.AppSettings["subscriptionId"]; }
if (String.IsNullOrEmpty(resourceGroup)) { resourceGroup = ConfigurationManager.AppSettings["resourceGroup"]; }
if (String.IsNullOrEmpty(cosmosDatabaseName)) { cosmosDatabaseName = ConfigurationManager.AppSettings["cosmosDatabaseName"]; } else { cosmosDatabaseName = "Orders"; }
if (String.IsNullOrEmpty(containerName)) { containerName = ConfigurationManager.AppSettings["containerName"]; } else { cosmosDatabaseName = "Orders"; }
if (String.IsNullOrEmpty(productsJsonFile)) { productsJsonFile = ConfigurationManager.AppSettings["productsJsonFile"]; } 
if (String.IsNullOrEmpty(storesJsonFile)) { storesJsonFile = ConfigurationManager.AppSettings["storesJsonFile"]; }

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
    // Get CosmostDB connection string using Azure Resource Manager APIs
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
    // Get database
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
    try
    {
        Console.WriteLine("Retrieving product information from Products container.");
        Container productsContainer = cosmosDB.GetContainer("Products");
        if (productsContainer != null)
        {
            using FeedIterator<Product> productIterator = productsContainer.GetItemQueryIterator<Product>(queryText: "SELECT * FROM Products");
            if (productIterator.HasMoreResults)
            {
                foreach (Product product in await productIterator.ReadNextAsync())
                {
                    productList.Add(product);
                }
            }
        }
    }
    catch (Exception)
    {
        Console.WriteLine("Products container not found in CosmosDB.");
    }
    // If Products container is not populated, generate new Products using below info or JSON file
    if (productList.Count <= 0)
    {
        Console.WriteLine("No products available to generate sample data. Importing products information from local JSON file.");

        // Import products frok JSON file in GitHub and use for sampling
        if (null != productsJsonFile && File.Exists(productsJsonFile))
        {
            var productsJsonText = File.ReadAllText(productsJsonFile);

            // Converto JSOn object
            productList = JsonConvert.DeserializeObject<List<Product>>(productsJsonText);
            if (null != productList && productList.Count > 0)
            {
                Console.WriteLine("Found {0} products in the container to generate sample data.", productList.Count);

                // Import products into CosmosDB to make them available for Azure Data Explorer reports
                Container productsContainer = await cosmosDB.CreateContainerIfNotExistsAsync(id: "Products", partitionKeyPath: "/ProductId");
                if (null != productsContainer)
                {
                    Console.WriteLine("Importing products data into CosmosDB container Products.");
                    foreach (Product product in productList)
                    {
                        var createdproduct = await productsContainer.CreateItemAsync<Product>(item: product);
                    }
                }
            }
        }
        else
        {
            System.Environment.Exit(-1);
        }
    }
    else
    {
        Console.WriteLine("Found {0} products in the container to generate sample data.", productList.Count);
    }

    // Get Store list to generate random orders from these stores
    try
    {
        Console.WriteLine("Retrieving stores information from Stores container.");
        Container storesContainer = cosmosDB.GetContainer("Stores");
        if (storesContainer != null)
        {
            using FeedIterator<Store> storeIterator = storesContainer.GetItemQueryIterator<Store>(queryText: "SELECT * FROM Stores");
            foreach (Store Store in await storeIterator.ReadNextAsync())
            {
                storeList.Add(Store);
            }
        }
    }
    catch (Exception)
    {

    }

    
    // Create new Stores list if no stores exist in the Stores container
    if (storeList.Count <= 0)
    {
        Console.WriteLine("No stores information available to generate sample data. Importing stores information from local JSON file.");
        // Import products frok JSON file in GitHub and use for sampling
        if (null != storesJsonFile && File.Exists(storesJsonFile))
        {
            var storesJsonText = File.ReadAllText(storesJsonFile);

            // Converto JSOn object
            storeList = JsonConvert.DeserializeObject<List<Store>>(storesJsonText);
            if (null != storeList && storeList.Count > 0)
            {
                Console.WriteLine("Found {0} stores in the container to generate sample data.", storeList.Count);

                // Import stores into CosmosDB to make them available for Azure Data Explorer reports
                Container storeContainer = await cosmosDB.CreateContainerIfNotExistsAsync(id: "Stores", partitionKeyPath: "/StoreId");
                if (null != storeContainer)
                {
                    Console.WriteLine("Importing stores data into CosmosDB container Stores.");

                    foreach (Store store in storeList)
                    {
                        var createdStore = await storeContainer.CreateItemAsync<Store>(item: store);
                    }
                }
            }
        }
        else
        {
            System.Environment.Exit(-1);
        }
    }
    else
    {
        Console.WriteLine("Found {0} stores in the container to generate sample data.", storeList.Count);
    }

    if (null == productList || null == storeList)
    {
        System.Environment.Exit(-1);
    }

    DateTime dataStartDate = DateTime.Now.AddDays(NoOfDays);
    Random random = new Random();
    Product[] products = productList.ToArray<Product>();
    Store[] stores = storeList.ToArray();

    do
    {
        Console.WriteLine("Generate sample data for: {0}", dataStartDate.ToString("MMM/dd/yyyyy"));

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
            order.storeId = stores[storeIndex].id;

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
