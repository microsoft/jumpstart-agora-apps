from azure.cosmos import CosmosClient
import time
import os
import psycopg2
import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sync_interval = int(os.environ.get('SYNCINTERVAL', 120)) #In seconds
now = datetime.datetime.now()

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

# Connect to PostgreSQL
cnxn = psycopg2.connect(**dbconfig)
cursor = cnxn.cursor()
logger.info("Connected to PostgreSQL")
client = CosmosClient(endpoint, key)
database = client.get_database_client(database_name)
container = database.get_container_client(container_name)
logger.info("Connected to Cosmos DB")

while True:
    logger.info("Polling Orders for unsynced records...")
    try:
        # Get all Order records where cloudSynced is NULL or FALSE
        query = "SELECT * FROM contoso.Orders WHERE cloudSynced IS NOT TRUE;"
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
            query = "UPDATE contoso.Orders SET cloudSynced = TRUE WHERE orderID = %s;"
            cursor.execute(query, (row[0],))
            logger.info("Order ID: %s synced to cloud", row[0])
            cnxn.commit()
    
    except psycopg2.Error as e:
        logger.error("An error occurred while executing a PostgreSQL query: %s", e)
        
        #Reconnecting PostgreSQL
        cnxn = psycopg2.connect(**dbconfig)
        cursor = cnxn.cursor()
    except Exception as e:
        logger.error("An error occurred while syncing data: %s", e)

    # Wait for sync_interval (seconds) before polling again
    time.sleep(sync_interval)