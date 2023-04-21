# Contoso Supermarket Point of Sale Helm Chart

## Install command
helm install --set cosmos.access_key="<Cosmos DB Access Key>" -n "<Namespace>" --create-namespace <Deployment Name> .

## Setable Values
| Value Name | Description | Required to be set | Default |
| --- | --- | --- | --- |
| postgres.username | The username to use when intilizaing the Postgres DB | No | "postgres" |
| postgres.password | The password to use when intilizaing the Postgres DB | No |  "admin123"
| cosmos.endpoint | The Cosmos DB Endpoint URL | Yes | "" |
| cosmos.database | The Cosmos DB Database Name | Yes | "" |
| cosmos.container | The Cosmos DB Container Name | Yes | "" |
| cosmos.access_key | The Cosmos DB Access Key | Yes |  |
| point-of-sale.title | The title of the point of sale website | No | "Contoso Supermarket" |
| point-of-sale.cameras-enabled | Flag to enable cameras | No | "False" |
| point-of-sale.cameras-url | The base URL for the camera feed, required if point-of-sale.cameras-enabled is "True" | No | "" |
| point-of-sale.new-category |  | No | "True" |
| point-of-sale.store-id | The ID of the store | No | 1 |
