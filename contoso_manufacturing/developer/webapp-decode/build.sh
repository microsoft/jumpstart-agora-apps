

#IF you are going to use docker to build and push the container, uncomment the following lines
echo $ACR

sudo docker login $ACR -u $ACRUSER -p $ACRPWD
sudo docker build -t $CONTAINER .
sudo docker tag $CONTAINER $ACR/$CONTAINER
sudo docker push $ACR/$CONTAINER

# Build the container in Azure Container Registry
# az login
#az account set -s $SUBSCRIPTION_ID
#az acr build --image  $ACR/$CONTAINER --registry $REGISTRY --file Dockerfile .

#Test the container
#docker run -e MQTT_BROKER=$MQTT_BROKER -e MQTT_PORT=$MQTT_PORT -e FRECUENCY=$FRECUENCY -t $CONTAINER