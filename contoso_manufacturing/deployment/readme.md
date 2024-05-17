# Deployment

The implementation sequence is defined as follows:


## Pre requisites

Use Azure IoT Operations or Mosquitto to individually test the components.

## step 1 - InfluxDb

```

# Apply the InfluxDB deployment configuration from the influxdb.yaml file. This will set up InfluxDB in your Kubernetes cluster.
kubectl apply -f influxdb.yaml

# Apply the ConfigMap for InfluxDB from the influxdb-configmap.yaml file. ConfigMaps are used to store non-confidential data in key-value pairs. This particular ConfigMap contain configuration settings for InfluxDB and the dashboard.
kubectl apply -f influxdb-configmap.yaml

# Apply a configuration to import dashboards into InfluxDB from the influxdb-import-dashboard.yaml file. This could be used to automatically set up dashboards in InfluxDB based on the specifications in the YAML file.

sudo mkdir /var/lib/influxdb2

sudo chmod 777 /var/lib/influxdb2

kubectl apply -f influxdb-import-dashboard.yaml

# Apply the deployment configuration for an MQTT simulator from the mqtt_simulator.yaml file. This simulator can be used for generating MQTT messages to test MQTT integrations or listeners in your environment.
kubectl apply -f mqtt_simulator.yaml

# Apply the deployment configuration for an MQTT listener from the mqtt-listener.yaml file. This listener acts as a subscriber to MQTT topics to process or store the incoming messages, potentially integrating with other services like InfluxDB.
kubectl apply -f mqtt-listener.yaml

# Apply the deployment configuration for an RTSP simulator from the rtsp-simulator.yaml file. This simulator can be used to mimic an RTSP feed, useful for testing video processing or streaming applications without the need for actual video sources.
kubectl apply -f rtsp-simulator.yaml

kubectl port-forward svc/virtual-rtsp 8554:8554

# Apply the deployment configuration for the 'decode' application from the decode.yaml file. This application is responsible for connecting to an RTSP feed, capturing frames, and potentially processing or forwarding those frames for further analysis or storage.
kubectl apply -f decode.yaml


```




kubectl delete service/influxdb -n azure-iot-operations
kubectl delete persistentvolume/influxdb-pv -n azure-iot-operations
kubectl delete persistentvolumeclaim/influxdb-pvc -n azure-iot-operations
kubectl describe pod/influxdb-0
kubectl delete job.batch/influxdb-setup -n azure-iot-operations
kubectl delete statefulset.apps/influxdb -n azure-iot-operations
