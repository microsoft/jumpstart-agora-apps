import os
import mysql.connector

class SqlConnector:
    sqlHost = ""
    sqlUsername = ""
    sqlPassword = ""
    sqlDatabase = ""

    def __init__(self):
        if os.environ.get('SQL_HOST'):
            self.sqlHost = str(os.environ['SQL_HOST'])

        if os.environ.get('SQL_USERNAME'):
            self.sqlUsername = str(os.environ['SQL_USERNAME'])
        
        if os.environ.get('SQL_PASSWORD'):
            self.sqlPassword = str(os.environ['SQL_PASSWORD'])

        if os.environ.get('SQL_DATABASE'):
            self.sqlDatabase = str(os.environ['SQL_DATABASE']) 

        self.connection = self.createServerConnection()
        if(self.connection != None):
            self.cursor = self.connection.cursor()
        else:
            print("Fail to establish MySQL database connection")

    def createServerConnection(self):
        connection = None
        try:
            connection = mysql.connector.connect(
                user= self.sqlUsername, 
                password= self.sqlPassword,
                host= self.sqlHost, 
                port=3306, 
                database= self.sqlDatabase, 
                ssl_disabled=True
            )

            print("MySQL Database connection successful")
        except Exception as ex:
            print(f"Error: '{ex}'")

        return connection

    def addPurchase(self, productId):
        try:
            query = "UPDATE `Stocks` SET `Sold` = `Sold` + 1, `Stock` = `Stock` - 1 WHERE `ProductID` = {}".format(productId)
            self.cursor.execute(query)
            self.connection.commit()
            if(self.cursor.rowcount == 1):
                return True
            else:
                return False
        except Exception as ex:
            print(f"Error: '{ex}'")
            return False

