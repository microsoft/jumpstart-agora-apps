# MQTT Simulator

This project contains a simulator that connects to an MQTT broker and simulates data transmission. To ensure its proper functioning, several environment variables need to be configured.

## Requirements

- Docker should be installed, along with the necessary tools to build and run containers.

## Environment Variables

The simulator requires you to set the following environment variables:

- `MQTT_BROKER`: Specifies the address of the MQTT broker.
- `MQTT_PORT`: Specifies the port of the MQTT broker.
- `FRECUENCY`: Determines the frequency at which data is sent.

For container construction, set the following variables:

- `ACR`: Name of the Azure Container Registry.
- `ACRUSER`: Azure Container Registry username.
- `ACRPWD`: Azure Container Registry password.
- `CONTAINER`: Name and tag of the container.
- `SUBSCRIPTION_ID`: Your Azure subscription ID.
- `REGISTRY`: Name of the registry in Azure.

## Configuration

1. Clone the repository onto your local machine.
2. In the project root, create a file named `simulator.env`.
3. Populate `simulator.env` with the following:

## Deployment

You'll find the deployment of the microservice in mqtt_simulator.yaml, located within the ../deployments/mqtt_simulator.yaml directory.

## Build Solution

Create a simulator.env file and add the following variables:

ACR=<your.azurecr.io>
ACRUSER=<your acr admin>
ACRPWD=<ACR password>
CONTAINER=mqtt-simulator:latest
MQTT_BROKER=<IP>
MQTT_PORT=1883
FRECUENCY=10
SUBSCRIPTION_ID=<Azure subscription ID>
REGISTRY=<ACR name>
