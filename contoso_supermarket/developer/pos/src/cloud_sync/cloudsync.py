from azure.cosmos import CosmosClient
import time
import os
import psycopg2


sync_interval = 120 #In seconds

# PostgreSQL connection settings
dbconfig = {
    "host": os.environ.get('SQL_HOST'),
    "user": os.environ.get('SQL_USERNAME'),
    "password": os.environ.get('SQL_PASSWORD'),
    "database": os.environ.get('SQL_DATABASE')

}

#Azure CosmosDB settings
endpoint = os.environ.get('COSMOSENDPOINT')
key = os.environ.get('COSMOSKEY')
database_name = os.environ.get('COSMOSDB')
container_name = os.environ.get('COSMOSCONTAINER')

# Connect to MySQL
cnxn = psycopg2.connect(**dbconfig)
cursor = cnxn.cursor()

# Connect to Azure Cosmos DB
client = CosmosClient(endpoint, key)
database = client.get_database_client(database_name)
container = database.get_container_client(container_name)

while True:
    # Get all records with cloudSynced = 0
    query = "SELECT * FROM contoso.Orders WHERE cloudSynced = 0"
    cursor.execute(query)
    rows = cursor.fetchall()

    # Sync each record to Azure Cosmos DB and set cloudSynced to True
    for row in rows:
        document = {
            'id': str(row[0]),
            'orderDate': str(row[1]),
            'orderdetails': row[2],
            'storeId': str(row[3]),
            'cloudSynced': True
        }
        container.upsert_item(document)
        query = "UPDATE contoso.Orders SET cloudSynced = 1 WHERE orderID = " + str(row[0])
        print("Order ID:",row[0],"synced to cloud")
        cursor.execute(query)
        cnxn.commit()

    # Wait for 2 minutes before syncing again
    time.sleep(sync_interval)
