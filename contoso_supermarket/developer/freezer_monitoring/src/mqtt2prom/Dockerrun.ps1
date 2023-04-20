
$image = "mqtt2prom"

docker rm -f $image;

docker run --name $image -d `
    --hostname=mqtt2prom `
    -p 9641:9641 `
    -v ./config.yaml:/data/config.yaml `
    js/$image
# /bin/bash -c "./entrypoint.sh; sleep 6000";
# docker exec -it $image bash
