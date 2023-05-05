using Npgsql;
using NpgsqlTypes;

namespace Contoso.Backend.Data.Services
{
    public class PostgreSqlService
    {
        private readonly string _connectionString;

        public PostgreSqlService(string connectionString)
        {
            _connectionString = connectionString;
        }

        public async Task<bool> TableHasValue(string tableName)
        {
            using var con = new NpgsqlConnection(_connectionString);
            await con.OpenAsync();
            var sql = $"select true from {tableName} limit 1;";
            using var cmd = new NpgsqlCommand(sql, con);
            var res = cmd.ExecuteScalar();
            await con.CloseAsync();

            return (bool)(res ?? false);
        }

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

        public async Task<DateTimeOffset> GetMaxCheckoutHistoryTimestamp()
        {
            using var con = new NpgsqlConnection(_connectionString);
            await con.OpenAsync();
            var sql = $"select max(timestamp) from contoso.checkout_history limit 1;";
            using var cmd = new NpgsqlCommand(sql, con);
            var res = cmd.ExecuteScalar();
            await con.CloseAsync();

            return (DateTime)(res ?? DateTime.MinValue);
        }

        public async Task<List<CheckoutHistory>> GetCheckoutHistory(DateTimeOffset? startDateTime = null, DateTimeOffset? endDateTime = null)
        {
            if (startDateTime == null) { startDateTime = DateTimeOffset.MinValue; }
            if (endDateTime == null) { endDateTime = DateTimeOffset.MaxValue; }

            using var con = new NpgsqlConnection(_connectionString);
            await con.OpenAsync();
            var sql = $@"select 
                            timestamp, 
                            checkout_id, 
                            checkout_type, 
                            queue_length, 
                            average_wait_time_seconds 
                        from contoso.checkout_history WHERE timestamp > @minTime AND timestamp <= @maxTime;";
            await using var cmd = new NpgsqlCommand(sql, con)
            {
                Parameters =
                {
                    new NpgsqlParameter("minTime",startDateTime),
                    new NpgsqlParameter("maxTime",endDateTime)
                }
            };

            List<CheckoutHistory> ret = new();

            using (var reader = cmd.ExecuteReader())
                while (reader.Read())
                {
                    CheckoutHistory item = new()
                    {
                        Timestamp = reader.GetDateTime(0),
                        CheckoutId = reader.GetInt32(1),
                        CheckoutType = (CheckoutType)reader.GetInt32(2),
                        QueueLength = reader.GetInt32(3),
                        AverageWaitTimeSeconds = reader.GetInt32(4)
                    };
                    ret.Add(item);
                }

            await con.CloseAsync();

            return ret;
        }


        public async Task<List<Checkout>> GetCheckouts()
        {
            using var con = new NpgsqlConnection(_connectionString);
            await con.OpenAsync();
            var sql = $@"SELECT id, type, avgprocessingtime, closed FROM contoso.checkout order by id;";
            await using var cmd = new NpgsqlCommand(sql, con);

            List<Checkout> checkouts = new List<Checkout>();

            using (var reader = cmd.ExecuteReader())
                while (reader.Read())
                {
                    int id = reader.GetInt32(0);
                    CheckoutType type = (CheckoutType)reader.GetInt32(1);
                    int avgProcessingTime = reader.GetInt32(2);
                    bool closed = reader.GetBoolean(3);
                    var checkout = new Checkout(id, type, avgProcessingTime, closed);
                    checkouts.Add(checkout);
                }
            await con.CloseAsync();

            return checkouts;
        }

        public async Task<Checkout> ToggleCheckout(int checkoutId)
        {
            using var con = new NpgsqlConnection(_connectionString);
            await con.OpenAsync();
            var sql = $@"UPDATE contoso.checkout
                SET closed = NOT closed
                WHERE id = @checkoutId
                RETURNING *;";
            await using var cmd = new NpgsqlCommand(sql, con)
            {
                Parameters =
                        {
                    new NpgsqlParameter("checkoutId", checkoutId)
                }
            };
            Checkout? checkout = null;

            using (var reader = cmd.ExecuteReader())
                if (reader.Read())
                {
                    int id = reader.GetInt32(0);
                    CheckoutType type = (CheckoutType)reader.GetInt32(1);
                    int avgProcessingTime = reader.GetInt32(2);
                    bool closed = reader.GetBoolean(3);
                    checkout = new Checkout(id, type, avgProcessingTime, closed);
                }
            await con.CloseAsync();

            if (checkout == null)
            {
                throw new Exception($"Checkout with id {checkoutId} not found");
            }

            return checkout;
        }

        public async Task<List<Product>> GetProducts()
        {
            using var con = new NpgsqlConnection(_connectionString);
            await con.OpenAsync();
            var sql = @"SELECT productid, name, description, price, stock, photopath FROM contoso.products ORDER BY productid;";
            await using var cmd = new NpgsqlCommand(sql, con);

            List<Product> ret = new();

            using (var reader = cmd.ExecuteReader())
                while (reader.Read())
                {
                    Product item = new()
                    {
                        Id = reader.GetInt32(0),
                        Name = reader.GetString(1),
                        Description = reader.GetString(2),
                        Price = reader.GetDouble(3),
                        Stock = reader.GetInt32(4),
                        PhotoPath = reader.GetString(5),
                    };
                    ret.Add(item);
                }

            await con.CloseAsync();

            return ret;
        }

        public async Task UpsertProducts(List<Product> products)
        {
            await using var con = new NpgsqlConnection(_connectionString);
            var tempTableName = "temptable";

            await con.OpenAsync();
            var sql = @$"CREATE TEMP TABLE {tempTableName}(productId SERIAL PRIMARY KEY, name text, description text, price numeric, stock int, photopath text, category text);";
            var cmd = new NpgsqlCommand(sql, con);
            await cmd.ExecuteNonQueryAsync();
            using var importer = con.BeginBinaryImport(
                       $"COPY {tempTableName} (productid, name, description, price, stock, photopath) FROM STDIN (FORMAT binary)");

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

        public async Task<bool> DeleteProduct(int productId)
        {
            using var con = new NpgsqlConnection(_connectionString);
            await con.OpenAsync();
            var sql = $"DELETE FROM contoso.products WHERE productid = @productId;";
            await using var cmd = new NpgsqlCommand(sql, con)
            {
                Parameters =
                {
                    new NpgsqlParameter("productId", productId)
                }
            };
            var res = cmd.ExecuteNonQuery();
            await con.CloseAsync();

            return true;
        }
    }
}
