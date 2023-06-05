
$image = "mqtt-simulator"

docker rm -f $image;

docker run --name $image -d `
    js/$image
