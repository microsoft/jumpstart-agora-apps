# Freezer Monitor

Easy-to-configure MQTT simulator written in [Python 3](https://www.python.org/) to simulate the sending of JSON objects from sensors or devices to a broker.

[Features](#features) •
[Important Notes](#important-notes) •
[Resources](#resources) •
[Tools](#tools) •
[Getting Started](#getting-started) •
[Configuration](#configuration) •
[Authors](#authors)

## Features
Freezer Monitor combines a MQTT broker and MQTT simulator to simulate the sending of JSON objects from sensors or devices to a broker. The simulator can be configured to send messages at a specified interval, and the broker can be configured to send messages to an IoT Hub.

## Important Notes

- Topics are *extremely sensitive* in Azure IoT. For example if you add:

    mqtt-simulator/settings.json: 
        
        "devices/ChicagoFreezer1/messages/events/freezer"
    
    then you must also add:

    mqtt-broker/ mosquitto.conf:
    
        topic devices/ChicagoFreezer1/messages/events/freezer out 1

- SAS Tokens need to be renewed periodically. Currently, you must run the `az iot hub generate-sas-token` command to get a new token and then update the mosquitto.conf file. This is a manual process that will be automated in the future.

- The simulator is currently configured to send messages to the broker on port 1883. The broker is configured to send messages to the IoT Hub on port 8883. If you change the port in the simulator, you must also change the port in the broker.

## Installing with Helm

`helm upgrade sensor-monitor sensor-monitor --version 1.0.0`

### Upgrade

`helm upgrade sensor-monitor sensor-monitor --version 1.0.1`

## Resources

- [Mosquitto MQTT broker to IoT Hub/IoT Edge](http://busbyland.com/mosquitto-mqtt-broker-to-iot-hub-iot-edge/)
- https://mosquitto.org/man/mosquitto-conf-5.html
- [Quickstart creates an Azure IoT Edge device on Linux | Microsoft Learn](https://learn.microsoft.com/azure/iot-edge/quickstart-linux?view=iotedge-1.4&viewFallbackFrom=iotedge-2020-11)
- [Quickstart - Send telemetry to Azure IoT Hub (CLI) quickstart | Microsoft Learn](https://learn.microsoft.com/azure/iot-hub/quickstart-send-telemetry-cli)

## Tools
- [IoT Explorer](https://github.com/Azure/azure-iot-explorer/releases)
    
    Lets you explore devices and their messages in Azure IoT Hub.

- [MQTT Explorer](http://mqtt-explorer.com/)
    
    Lets you explore devices and their messages in a local MQTT broker.





## Local AKS EE deployment

1. tag the images for ACR

    ```shell
    docker tag js/mqtt-broker jumpstartagora.azurecr.io/contoso-supermarket/mqtt-broker
    docker tag js/mqtt-simulator jumpstartagora.azurecr.io/contoso-supermarket/mqtt-simulator
    ```

    ### Updated naming conventions for jumpstart
    
    - jumpstartagora.azurecr.io/contoso-supermarket/<SERVICE-NAME>. For example:
        
        `docker tag js/mqtt-broker jumpstartagora.azurecr.io/contoso-supermarket/mqtt-broker`

    - Please use hyphens and not underscore. In the case of the pos service, no need since it's only one word.
        
        `docker tag js/pos jumpstartagora.azurecr.io/contoso-supermarket/pos` 
    
    - The "latest" tag is the default. In case you want to test various versions, please tag it accordingly. For example:

        `jumpstartagora.azurecr.io/contoso-supermarket/freezer-monitor:0.1.1`


2. Push images to MCR
    ```shell
    docker push jumpstartagora.azurecr.io/contoso-supermarket/mqtt-broker
    docker push jumpstartagora.azurecr.io/contoso-supermarket/mqtt-simulator
    ```

    ### Local AKS EE deployment - All-in-one commands for convenience
    
    ```shell
    docker build -t js/mqtt-broker .\mqtt-broker\.; docker tag js/mqtt-broker jumpstartagora.azurecr.io/contoso-supermarket ; docker push jumpstartagora.azurecr.io/contoso-supermarket
    kubectl rollout restart deployment mqtt-broker
    
    docker build -t js/mqtt-simulator .\mqtt-simulator\.; docker tag js/mqtt-simulator jumpstartagora.azurecr.io/contoso-supermarket/mqtt-simulator ; docker push jumpstartagora.azurecr.io/contoso-supermarket/mqtt-simulator
    kubectl rollout restart deployment mqtt-simulator
    ```

    #### Note: See OneNote for output with appId, password, tenant
    
4. Create a secret in the cluster to store the service principal credentials for the ACR registry

    ```powershell
    kubectl create secret docker-registry $mcr_name `
        --namespace default `
        --docker-server $mcr_url `
        --docker-username $sp.appId `
        --docker-password $sp.password
    ```
