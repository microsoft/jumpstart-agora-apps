source decode.env

ACR=agoraarmbladev.azurecr.io
ACRUSER=agoraarmbladev
ACRPWD=


CONTAINER=decode-svc:1.6

docker login $ACR -u $ACRUSER -p $ACRPWD

docker build -t $CONTAINER .
docker tag $CONTAINER $ACR/$CONTAINER
docker push $ACR/$CONTAINER

# Build the container
#az login
#az account set -s $SUBSCRIPTION_ID
#az acr build --image  $ACR/$CONTAINER --registry $REGISTRY --file Dockerfile .

# sudo docker run -e rtsp_url="rtsp://10.211.55.5:8554/stream" -e save_path="frames" -p 80:80 -it agoraarmbladev.azurecr.io/decode-svc:1.1
Test the container
docker run -e rtsp_url="rtsp://127.0.0.1:8554/stream" -e save_path="frames" -p 80:80 -it agoraarmbladev.azurecr.io/decode-svc:1.6