
$image = "mqtt-simulator"

docker rm -f $image;

docker run --name $image -d `
    js/$image
# /bin/bash -c "./entrypoint.sh; sleep 6000";
# docker exec -it $image bash
