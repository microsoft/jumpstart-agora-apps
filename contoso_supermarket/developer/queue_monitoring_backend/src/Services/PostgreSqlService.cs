using Npgsql;
using NpgsqlTypes;

namespace Contoso.Backend.Data.Services
{
    public class PostgreSqlService
    {
        private readonly ILogger<PostgreSqlService> _logger;
        private readonly string _connectionString;

        public PostgreSqlService(ILogger<PostgreSqlService> logger, string connectionString)
        {
            _logger = logger;
            _connectionString = connectionString;
        }

        // Method to check if a table has any values
        public async Task<bool> TableHasValue(string tableName)
        {
            using var con = new NpgsqlConnection(_connectionString);
            await con.OpenAsync();
            // Define the SQL query to check if the specified table has any values
            var sql = $"SELECT true FROM {tableName} LIMIT 1;";
            using var cmd = new NpgsqlCommand(sql, con);
            var res = cmd.ExecuteScalar();
            await con.CloseAsync();

            // Return true if the result is not null, otherwise return false
            return (bool)(res ?? false);
        }

        // Method to perform a bulk upsert of checkout history data
        public async Task BulkUpsertCheckoutHistory(List<CheckoutHistory> history)
        {
            await using var con = new NpgsqlConnection(_connectionString);
            await con.OpenAsync();

            // Create a temporary table to hold the data for upsert
            using (var cmd = new NpgsqlCommand("CREATE TEMP TABLE temp_table (LIKE contoso.checkout_history INCLUDING DEFAULTS)", con))
                cmd.ExecuteNonQuery();

            // Copy the data into the temporary table
            using (var importer = con.BeginBinaryImport("COPY temp_table (timestamp, checkout_id, checkout_type, queue_length, average_wait_time_seconds) FROM STDIN (FORMAT binary)"))
            {
                foreach (var element in history)
                {
                    await importer.StartRowAsync();
                    await importer.WriteAsync(element.Timestamp, NpgsqlDbType.TimestampTz);
                    await importer.WriteAsync(element.CheckoutId, NpgsqlDbType.Integer);
                    await importer.WriteAsync((int)element.CheckoutType, NpgsqlDbType.Integer);
                    await importer.WriteAsync(element.QueueLength, NpgsqlDbType.Integer);
                    await importer.WriteAsync(element.AverageWaitTimeSeconds, NpgsqlDbType.Integer);
                }
                await importer.CompleteAsync();
            }

            // Perform the upsert from the temporary table into the target table
            using (var cmd = new NpgsqlCommand(@"INSERT INTO contoso.checkout_history (timestamp, checkout_id, checkout_type, queue_length, average_wait_time_seconds)
                                        SELECT timestamp, checkout_id, checkout_type, queue_length, average_wait_time_seconds FROM temp_table
                                        ON CONFLICT (timestamp, checkout_id) DO UPDATE SET
                                        checkout_type = EXCLUDED.checkout_type,
                                        queue_length = EXCLUDED.queue_length,
                                        average_wait_time_seconds = EXCLUDED.average_wait_time_seconds", con))
                cmd.ExecuteNonQuery();
        }

        public async Task DeleteOldCheckoutHistory(int days)
        {
            using var con = new NpgsqlConnection(_connectionString);
            await con.OpenAsync();
            // Define the SQL query to delete rows from the contoso.checkout_history table
            // where the timestamp column is greater than the current date minus the specified number of days
            var sql = "DELETE FROM contoso.checkout_history WHERE timestamp < CURRENT_DATE - INTERVAL '1 day' * @days;";
            // Create a new command using the SQL query and the database connection
            using var cmd = new NpgsqlCommand(sql, con);
            // Add the parameter to the command
            cmd.Parameters.AddWithValue("days", days);
            // Execute the command and get the number of rows affected
            var rowsAffected = await cmd.ExecuteNonQueryAsync();

            // Log if any rows were deleted
            if (rowsAffected > 0)
            {
                _logger.LogInformation($"{rowsAffected} rows were deleted FROM the contoso.checkout_history table.");
            }

            await con.CloseAsync();
        }

        // Method to get the maximum timestamp value from the checkout history table
        public async Task<DateTimeOffset> GetMaxCheckoutHistoryTimestamp()
        {
            using var con = new NpgsqlConnection(_connectionString);
            await con.OpenAsync();
            // Define the SQL query to get the maximum timestamp value from the contoso.checkout_history table
            var sql = $"SELECT max(timestamp) FROM contoso.checkout_history LIMIT 1;";
            // Create a new command using the SQL query and the database connection
            using var cmd = new NpgsqlCommand(sql, con);
            // Execute the command and get the result
            var res = cmd.ExecuteScalar();

            await con.CloseAsync();

            // Return the result as a DateTime value, or return DateTime.MinValue if the result is null
            return (DateTime)(res ?? DateTime.MinValue);
        }

        // Method to get checkout history data within a specified date range
        public async Task<List<CheckoutHistory>> GetCheckoutHistory(DateTimeOffset? startDateTime = null, DateTimeOffset? endDateTime = null)
        {
            // Set default values for startDateTime and endDateTime if they are null
            if (startDateTime == null) { startDateTime = DateTimeOffset.MinValue; }
            if (endDateTime == null) { endDateTime = DateTimeOffset.MaxValue; }

            using var con = new NpgsqlConnection(_connectionString);
            await con.OpenAsync();
            // Define the SQL query to get checkout history data within a specified date range
            var sql = $@"SELECT 
                            timestamp, 
                            checkout_id, 
                            checkout_type, 
                            queue_length, 
                            average_wait_time_seconds 
                        FROM contoso.checkout_history WHERE timestamp > @minTime AND timestamp <= @maxTime;";
            // Create a new command using the SQL query and the database connection
            await using var cmd = new NpgsqlCommand(sql, con)
            {
                // Add the parameters to the command
                Parameters =
                {
                    new NpgsqlParameter("minTime",startDateTime),
                    new NpgsqlParameter("maxTime",endDateTime)
                }
            };

            // Create a new list to hold the checkout history data
            List<CheckoutHistory> ret = new();

            // Execute the command and get the result
            using (var reader = cmd.ExecuteReader())
                while (reader.Read())
                {
                    // Create a new CheckoutHistory object for each row in the result
                    CheckoutHistory item = new()
                    {
                        Timestamp = reader.GetDateTime(0),
                        CheckoutId = reader.GetInt32(1),
                        CheckoutType = (CheckoutType)reader.GetInt32(2),
                        QueueLength = reader.GetInt32(3),
                        AverageWaitTimeSeconds = reader.GetInt32(4)
                    };
                    // Add the CheckoutHistory object to the list
                    ret.Add(item);
                }


            await con.CloseAsync();

            // Return the list of checkout history data
            return ret;
        }

        // Method to get a list of all checkouts
        public async Task<List<Checkout>> GetCheckouts()
        {
            using var con = new NpgsqlConnection(_connectionString);
            await con.OpenAsync();
            // Define the SQL query to get all checkouts from the contoso.checkout table
            var sql = $@"SELECT id, type, avgprocessingtime, closed FROM contoso.checkout order by id;";
            // Create a new command using the SQL query and the database connection
            await using var cmd = new NpgsqlCommand(sql, con);

            // Create a new list to hold the checkouts
            List<Checkout> checkouts = new List<Checkout>();

            // Execute the command and get the result
            using (var reader = cmd.ExecuteReader())
                while (reader.Read())
                {
                    // Get the values from each column in the row
                    int id = reader.GetInt32(0);
                    CheckoutType type = (CheckoutType)reader.GetInt32(1);
                    int avgProcessingTime = reader.GetInt32(2);
                    bool closed = reader.GetBoolean(3);
                    // Create a new Checkout object using the values from the row
                    var checkout = new Checkout(id, type, avgProcessingTime, closed);
                    // Add the Checkout object to the list
                    checkouts.Add(checkout);
                }
            await con.CloseAsync();

            // Return the list of checkouts
            return checkouts;
        }

        // Method to toggle the closed status of a checkout
        public async Task<Checkout> ToggleCheckout(int checkoutId)
        {
            using var con = new NpgsqlConnection(_connectionString);
            await con.OpenAsync();
            // Define the SQL query to update the closed status of a checkout in the contoso.checkout table
            var sql = $@"UPDATE contoso.checkout
                SET closed = NOT closed
                WHERE id = @checkoutId
                RETURNING *;";
            // Create a new command using the SQL query and the database connection
            await using var cmd = new NpgsqlCommand(sql, con)
            {
                // Add the parameter to the command
                Parameters =
                        {
                    new NpgsqlParameter("checkoutId", checkoutId)
                }
            };
            Checkout? checkout = null;

            // Execute the command and get the result
            using (var reader = cmd.ExecuteReader())
                if (reader.Read())
                {
                    // Get the values from each column in the row
                    int id = reader.GetInt32(0);
                    CheckoutType type = (CheckoutType)reader.GetInt32(1);
                    int avgProcessingTime = reader.GetInt32(2);
                    bool closed = reader.GetBoolean(3);
                    // Create a new Checkout object using the values from the row
                    checkout = new Checkout(id, type, avgProcessingTime, closed);
                }

            await con.CloseAsync();

            // If the checkout was not found, throw an exception
            if (checkout == null)
            {
                throw new Exception($"Checkout with id {checkoutId} not found");
            }

            // Return the updated checkout
            return checkout;
        }

        // Method to get a list of all products
        public async Task<List<Product>> GetProducts()
        {
            using var con = new NpgsqlConnection(_connectionString);
            await con.OpenAsync();
            // Define the SQL query to get all products from the contoso.products table
            var sql = @"SELECT productid, name, description, price, stock, photopath FROM contoso.products ORDER BY productid;";
            // Create a new command using the SQL query and the database connection
            await using var cmd = new NpgsqlCommand(sql, con);

            // Create a new list to hold the products
            List<Product> ret = new();

            // Execute the command and get the result
            using (var reader = cmd.ExecuteReader())
                while (reader.Read())
                {
                    // Create a new Product object for each row in the result
                    Product item = new()
                    {
                        Id = reader.GetInt32(0),
                        Name = reader.GetString(1),
                        Description = reader.GetString(2),
                        Price = reader.GetDouble(3),
                        Stock = reader.GetInt32(4),
                        PhotoPath = reader.GetString(5),
                    };
                    // Add the Product object to the list
                    ret.Add(item);
                }


            await con.CloseAsync();

            // Return the list of products
            return ret;
        }

        // Method to perform an upsert of product data
        public async Task UpsertProducts(List<Product> products)
        {
            await using var con = new NpgsqlConnection(_connectionString);
            var tempTableName = "temptable";

            await con.OpenAsync();
            // Define the SQL query to create a temporary table to hold the data for upsert
            var sql = @$"CREATE TEMP TABLE
                {tempTableName}(productId SERIAL PRIMARY KEY, name text, description text, price numeric, stock int, photopath text, category text);";
            var cmd = new NpgsqlCommand(sql, con);
            await cmd.ExecuteNonQueryAsync();
            using var importer = con.BeginBinaryImport(
                       $"COPY {tempTableName} (productid, name, description, price, stock, photopath) FROM STDIN (FORMAT binary)");

            // Copy the data into the temporary table
            foreach (var element in products)
            {
                await importer.StartRowAsync();
                await importer.WriteAsync(element.Id, NpgsqlDbType.Integer);
                await importer.WriteAsync(element.Name, NpgsqlDbType.Varchar);
                await importer.WriteAsync(element.Description, NpgsqlDbType.Varchar);
                await importer.WriteAsync(element.Price, NpgsqlDbType.Numeric);
                await importer.WriteAsync(element.Stock, NpgsqlDbType.Integer);
                await importer.WriteAsync(element.PhotoPath, NpgsqlDbType.Varchar);
            }

            await importer.CompleteAsync();
            await importer.CloseAsync();
            // Define the SQL query to perform the upsert from the temporary table into the target table
            var merge = @$"
                MERGE INTO contoso.products p
                USING {tempTableName} t
                ON t.productid = p.productid
                WHEN NOT MATCHED THEN
                    INSERT VALUES(t.productid, t.name, t.description, t.price, t.stock, t.photopath)
                WHEN MATCHED THEN
                    UPDATE SET name = t.name, description = t.description, price = t.price, stock = t.stock, photopath = t.photopath
                ;";
            var cmdMerge = new NpgsqlCommand(merge, con);
            await cmdMerge.ExecuteNonQueryAsync();

            await con.CloseAsync();
            return;
        }

        // Method to delete a product by its ID
        public async Task<bool> DeleteProduct(int productId)
        {
            using var con = new NpgsqlConnection(_connectionString);
            await con.OpenAsync();
            // Define the SQL query to delete a row from the contoso.products table where the productid column matches the specified productId
            var sql = $"DELETE FROM contoso.products WHERE productid = @productId;";
            // Create a new command using the SQL query and the database connection
            await using var cmd = new NpgsqlCommand(sql, con)
            {
                // Add the parameter to the command
                Parameters =
                {
                    new NpgsqlParameter("productId", productId)
                }
            };
            // Execute the command and get the number of rows affected
            var res = cmd.ExecuteNonQuery();

            await con.CloseAsync();

            // Return true if the operation was successful
            return true;
        }
    }
}