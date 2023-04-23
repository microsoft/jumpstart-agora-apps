# Contoso Supermarket Point of Sale Helm Chart

## Install command
helm install --set cosmos.access_key="<Cosmos DB Access Key>" -n "<Namespace>" --create-namespace <Deployment Name> .

## Setable Values
| Value Name | Description | Required to be set | Default |
| --- | --- | --- | --- |
| timezone | The timezone for the application to use. Uses Microsoft Time Zone strings | No | "Pacific Standard Time" |
| postgres.username | The username to use when intilizaing the Postgres DB | No | "postgres" |
| postgres.password | The password to use when intilizaing the Postgres DB | No | "admin123" |
| cosmos.endpoint | The Cosmos DB Endpoint URL | Yes |  |
| cosmos.database | The Cosmos DB Database Name | Yes |  |
| cosmos.container | The Cosmos DB Container Name | Yes |  |
| cosmos.access_key | The Cosmos DB Access Key | Yes |  |
| point_of_sale.title | The title of the point of sale website | No | "Contoso Supermarket" |
| point_of_sale.cameras_enabled | Flag to enable cameras | No | "False" |
| point_of_sale.cameras_url | The base URL for the camera feed, required if point_of_sale.cameras_enabled is "True" | No | "" |
| point_of_sale.new_category |  | No | "True" |
| point_of_sale.store_id | The ID of the store | No | 1 |
