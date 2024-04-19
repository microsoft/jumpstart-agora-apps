source mqtt-listener.env

docker login $ACR -u $ACRUSER -p $ACRPWD

docker build -t $CONTAINER .
docker tag $CONTAINER $ACR/$CONTAINER
docker push $ACR/$CONTAINER

# Build the container
#az login
#az account set -s $SUBSCRIPTION_ID
#az acr build --image  $ACR/$CONTAINER --registry $REGISTRY --file Dockerfile .

#Test the container
#sudo docker run -e MQTT_BROKER="10.211.55.5" -e MQTT_TOPIC1="topic/productionline" -e MQTT_TOPIC2="topic/magnemotion" -e INFLUX_URL="http://10.211.55.5:8086" -e INFLUX_TOKEN="secret-token" -e INFLUX_ORG="InfluxData" -e INFLUX_BUCKET="manufacturing" -t $CONTAINER

#sudo docker run -e MQTT_BROKER="10.211.55.5" -e MQTT_TOPIC1="topic/weldingrobot" -e MQTT_TOPIC2="topic/assemblybatteries" -e MQTT_TOPIC3="topic/assemblyline" -e INFLUX_URL="http://10.211.55.5:8086" -e INFLUX_TOKEN="secret-token" -e INFLUX_ORG="InfluxData" -e INFLUX_BUCKET="manufacturing" -it agoraarmbladev.azurecr.io/mqtt-listener:2.0