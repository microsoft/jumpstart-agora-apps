source decode.env

CONTAINER=decode-svc:1.5

sudo docker login $ACR -u $ACRUSER -p $ACRPWD

sudo docker build -t $CONTAINER .
sudo docker tag $CONTAINER $ACR/$CONTAINER
sudo docker push $ACR/$CONTAINER

# Build the container
#az login
#az account set -s $SUBSCRIPTION_ID
#az acr build --image  $ACR/$CONTAINER --registry $REGISTRY --file Dockerfile .

# sudo docker run -e rtsp_url="rtsp://10.211.55.5:8554/stream" -e save_path="frames" -p 80:80 -it agoraarmbladev.azurecr.io/decode-svc:1.1