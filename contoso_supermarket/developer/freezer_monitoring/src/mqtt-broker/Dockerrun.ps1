$image = "mqtt-broker"

docker rm -f $image;

docker run --name $image -d `
    --hostname=mqtt-broker `
    -p 1883:1883 `
    js/$image 
    