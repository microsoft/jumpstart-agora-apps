# Contoso Supermarket Point of Sale Helm Chart

## Install command
helm install --set cosmos.access_key="<Cosmos DB Access Key>" -n "<Namespace>" --create-namespace <Deployment Name> .

## Setable Values
| Value Name | Description | Required to be set | Default
| postgres.username | The username to use when intilizaing the Postgres DB | No | "postgres" |
| postgres.password | The password to use when intilizaing the Postgres DB | No |  "admin123"
| cosmos.endpoint | The Cosmos DB Endpoint URL | Yes | "" |
| cosmos.database | The Cosmos DB Database Name | Yes | "" |
| cosmos.container | The Cosmos DB Container Name | Yes | "" |
| cosmos.access_key | The Cosmos DB Access Key | Yes |  |

