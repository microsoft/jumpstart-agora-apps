
$image = "mqtt-broker"

docker rm -f $image;

docker run --name $image -d `
    --hostname=mqtt-broker `
    -p 1883:1883 `
    js/$image 
#     /bin/sh -c "/usr/sbin/mosquitto -c /mosquitto.conf; sleep 6000"
#     /bin/sh -c "./entrypoint.sh; sleep 6000"; `
# docker exec -it $image bash

