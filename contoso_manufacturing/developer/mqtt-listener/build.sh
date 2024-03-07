source mqtt-listener.env

#sudo docker login $ACR -u $ACRUSER -p $ACRPWD

#sudo docker build -t $CONTAINER .
#sudo docker tag $CONTAINER $ACR/$CONTAINER
#sudo docker push $ACR/$CONTAINER

# Build the container
az login
az account set -s $SUBSCRIPTION_ID
az acr build --image  $ACR/$CONTAINER --registry $REGISTRY --file Dockerfile .

#Test the container
#sudo docker run -e MQTT_BROKER="10.211.55.23" -e MQTT_TOPIC1="topic/productionline" -e MQTT_TOPIC2="topic/magnemotion" -e INFLUX_URL="http://10.211.55.23:8086" -e INFLUX_TOKEN="secret-token" -e INFLUX_ORG="InfluxData" -e INFLUX_BUCKET="manufacturing" -t $CONTAINER