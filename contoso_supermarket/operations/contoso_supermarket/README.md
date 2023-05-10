# Contoso Supermarket Point of Sale Helm Chart
## Install command

Example command for installation using powershell:
```powershell
helm install contoso-supermarket -n "contoso" --create-namespace . `
--set postgres.password="<PostgresPassword>" `
--set cosmos.access_key="<ComsmosDbAccessKey>" `
--set cosmos.endpoint="<ComsmosDbEndpoint>" `
--set point_of_sale.store_id="1" `
--set point_of_sale.store_location="Seattle"
```

Example command for upgrading deployment using powershell - E.g. setting a new variable:
```powershell
helm upgrade contoso-supermarket -n "contoso" . `
--set postgres.password="<PostgresPassword>" `
--set cosmos.access_key="<ComsmosDbAccessKey>" `
--set cosmos.endpoint="<ComsmosDbEndpoint>" `
--set point_of_sale.store_id="1" `
--set point_of_sale.store_location="Seattle" `
--set-string point_of_sale.holiday_banner="True" `
--set queue_monitoring_frontend.live_view_enabled="True"
```

## Setable Values
| Value Name | Description | Required to be set | Default |
| --- | --- | --- | --- |
| postgres.password | The password to use when intilizaing the Postgres DB | Yes |  |
| postgres.username | The username to use when intilizaing the Postgres DB | No | "postgres" |
| cosmos.access_key | The Cosmos DB Access Key | Yes |  |
| cosmos.endpoint | The Cosmos DB Endpoint URL | Yes |  |
| cosmos.database | The Cosmos DB Database Name | No | "contoso" |
| cosmos.container | The Cosmos DB Container Name | No | "pos"  |
| point_of_sale.store_id | The ID of the store | Yes | |
| point_of_sale.store_location | The location of the store | Yes | |
| point_of_sale.holiday_banner | Updates the banner to show holiday theme. "True" shows the banner.  | No | "False" |
| point_of_sale.title | The title of the point of sale website | No | "Contoso Supermarket" |
| point_of_sale.cameras_enabled | Flag to enable cameras | No | "False" |
| point_of_sale.cameras_url | The base URL for the camera feed, required if point_of_sale.cameras_enabled is "True" | No | "" |
| point_of_sale.new_category |  | No | "True" |
| queue_monitoring_frontend.live_view_enabled | Enables or disables the live view  | No | "False" |
