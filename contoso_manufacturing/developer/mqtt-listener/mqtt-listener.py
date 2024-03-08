import paho.mqtt.client as mqtt
import json
import os
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS


mqtt_broker = os.environ.get("MQTT_BROKER", "")
mqtt_port = int(os.environ.get("MQTT_PORT", ""))
mqtt_topic1 = os.environ.get("MQTT_TOPIC1", "")
mqtt_topic2 = os.environ.get("MQTT_TOPIC2", "")

influx_url = os.environ.get("INFLUX_URL", "")
influx_token = os.environ.get("INFLUX_TOKEN", "")
influx_org = os.environ.get("INFLUX_ORG", "")
influx_bucket = os.environ.get("INFLUX_BUCKET", "")


# Callback when the client receives a CONNACK response from the server
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    # Subscribe to both topics
    client.subscribe([(mqtt_topic1, 0), (mqtt_topic2, 0)])

# Callback for when a message is received from the server
def on_message(client, userdata, msg):
    print(f"Message received `{msg.topic}`: {msg.payload.decode('utf-8')}")

    # Parse the JSON data from the message payload
    json_data = json.loads(msg.payload.decode('utf-8'))
    data = json_data.get("data")

    if data:
        point = Point(msg.topic).time(data.get("Timestamp"), WritePrecision.NS)
        for key, value in data.items():
            if key != "Timestamp":  # Exclude the timestamp
                point = point.field(key, value)
        write_api.write(bucket=influx_bucket, record=point)

# Initialize the InfluxDB Client with username and password
def main():

    # Get configurations

    print("Initializing MQTT listener...")
    print("MQTT Broker: ", mqtt_broker)
    print("MQTT Port: ", mqtt_port)
    print("MQTT Topic1: ", mqtt_topic1)
    print("MQTT Topic2: ", mqtt_topic2)
    print("InfluxDB URL: ", influx_url)
    print("InfluxDB Token: ", influx_token)
    print("InfluxDB Org: ", influx_org)
    print("InfluxDB Bucket: ", influx_bucket)

    # Initialize the InfluxDB Client
    print("Initializing InfluxDB Client...")
    client_influx = InfluxDBClient(url=influx_url, token=influx_token, org=influx_org)
    global write_api 
    write_api = client_influx.write_api(write_options=SYNCHRONOUS)

    # Initialize MQTT Client
    print("Initializing MQTT Client...")
    client_mqtt = mqtt.Client()
    client_mqtt.on_connect = on_connect
    client_mqtt.on_message = on_message

    # Connect to MQTT Broker
    client_mqtt.connect(mqtt_broker, mqtt_port, 60)

    # Process messages indefinitely
    client_mqtt.loop_forever()

if __name__ == "__main__":
    main()
