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



## Local testing process of the broker and simulator

- get a sas token - expires every 60 minutes by default but can be overridden with the `--duration` parameter

    ```powershell
    ((az iot hub generate-sas-token -g charris-iot1 -d chicagoFreezer2 --duration $(60*20*24*365) -n charris-iot1 -o json) | convertfrom-json).sas | set-clipboard
    ```

- update the mosquitto.conf file with the new token

    ```bash
    sed -i 's/SharedAccessSignature sr=charris-iot1.azure-devices.net%2FchicagoFreezer2&sig=.*&se=.*&skn=iothubowner/SharedAccessSignature sr=charris-iot1.azure-devices.net%2FchicagoFreezer2&sig=REPLACE_WITH_NEW_TOKEN&se=REPLACE_WITH_NEW_TOKEN&skn=iothubowner/g' mqtt-broker/mosquitto.conf
    ```

- from the freezer_monitoring\src folder

- start the broker
    `docker build -t js/mqtt-broker:latest .\mqtt-broker\.; .\mqtt-broker\Dockerrun.ps1`

- start the simulator
    `docker build -t js/mqtt-simulator:latest .\mqtt-simulator\.; .\mqtt-simulator\Dockerrun.ps1`

- install mosquitto client
    `apt install mosquitto -y`

- subscribe
    `mosquitto_sub -h localhost -p 1883 -u sensor123 -P sensor123 -v -t freezer/+`
    or http://mqtt-explorer.com/ - connect and then click the little green graph icon next to the value on the right side   

### TODO - Need to test these next two - they were auto-generated by Copilot
- update the mosquitto.conf file with the new device name

    ```bash
    sed -i 's/devices\/chicagoFreezer2\/messages\/events\/freezer/devices\/chicagoFreezer2\/messages\/events\/freezer/g' mqtt-broker/mosquitto.conf
    ```
- update the settings.json file with the new device name

    ```bash
    sed -i 's/devices\/chicagoFreezer2\/messages\/events\/freezer/devices\/chicagoFreezer2\/messages\/events\/freezer/g' mqtt-simulator/settings.json
    ```


## Cloud testing process

### Test your own messages with `mosquitto_pub`

- Follow one of the [Resources](#resources) links above to get the Baltimore.pem file

    ```shell
    export sas_token=$(az iot hub generate-sas-token -g charris-iot1 -d myEdgeDevice --duration $(60*20*24*365) -n charris-iot1 -o json | jq -r '.sas')

    mosquitto_pub -t "devices/myEdgeDevice/messages/events/freezer" -i "myEdgeDevice" -u "charris-iot1.azure-devices.net/myEdgeDevice/?api-version=2020-09-30" -P $sas_token -h "charris-iot1.azure-devices.net" -V mqttv311 -p 8883 --cafile Baltimore.pem -m 'My Awesome Message' -d
    ```

### View the messages in IoT Hub

- monitor what's coming into IoT hub
    `az iot hub monitor-events --output table --device-id myEdgeDevice --hub-name charris-iot1 --output json`

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

3. Create a service principal to access the MCR registry

    ```powershell
    $mcr_sub = "2554f64d-0419-4e39-8121-5e01270578ea"
    $mcr_rg = "charris-agora"
    $mcr_name = "charrisagoracr"
    $mcr_url = "charrisagoracr.azurecr.io"
    $sp_name = "charris-iot1"

    $sp = az ad sp create-for-rbac `
        --name $sp_name `
        --role Contributor `
        --scopes /subscriptions/$mcr_sub/resourcegroups/$mcr_rg/providers/Microsoft.ContainerRegistry/registries/$mcr_name | convertfrom-json
    ```
    #### Note: See OneNote for output with appId, password, tenant
    
4. Create a secret in the cluster to store the service principal credentials for the ACR registry

    ```powershell
    kubectl create secret docker-registry $mcr_name `
        --namespace default `
        --docker-server $mcr_url `
        --docker-username $sp.appId `
        --docker-password $sp.password


## Azure Setup

1. https://techcommunity.microsoft.com/t5/internet-of-things-blog/mosquitto-client-tools-and-azure-iot-hub-the-beginning-of/ba-p/2824717
2. 
3. Ignore following...
4. `$LOCATION = "eastus"`
5. `$RESOURCE_GROUP_NAME = "charris-iot1"`
6. `$HUB_NAME = $RESOURCE_GROUP_NAME`
7. `az group create --location $location --name $RESOURCE_GROUP_NAME`
8. foreach $DEVICE in $DEVICES
    `az iot hub device-identity create --device-id $DEVICE --edge-enabled --hub-name $HUB_NAME`
9. View connection string
   1. `az iot hub device-identity connection-string show --device-id $DEVICE --hub-name $HUB_NAME`
10. Configure Broker to send to IoT Hub
  - foreach device: update remote_password in mqtt-broker/mosquitto.conf
  `az iot hub generate-sas-token --device-id chicagoFreezer1 --hub-name charris-iot1 --duration (60*60*24*365) --query sas -o tsv`




Elevated PowerShell
    1. Install AzureIoTEdge

    ```powershell
    $msiPath = $([io.Path]::Combine($env:TEMP, 'AzureIoTEdge.msi'))
    $ProgressPreference = 'SilentlyContinue'
    Invoke-WebRequest "https://aka.ms/AzEFLOWMSI_1_4_LTS_X64" -OutFile $msiPath
    Start-Process -Wait msiexec -ArgumentList "/i","$([io.Path]::Combine($env:TEMP, 'AzureIoTEdge.msi'))","/qn"
    ```

### Debug mqtt-broker

`apk update`
`apk add nano`


## Local Registry Deployment
2. deploy the images to the local registry

    ```powershell
    kubectl apply -f .\mqtt-broker-pod.yaml
    kubectl apply -f .\mqtt-broker-service.yaml
    kubectl apply -f .\mqtt-simulator-pod.yaml
    ```