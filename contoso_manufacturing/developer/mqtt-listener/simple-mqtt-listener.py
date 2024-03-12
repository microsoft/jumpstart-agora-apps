import paho.mqtt.client as mqtt
import json
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import random


# MQTT Client configuration
mqtt_broker = "127.0.0.1"
mqtt_port = 1883
mqtt_topic1 = "topic/productionline"
mqtt_topic2 = "topic/magnemotion"

# InfluxDB Client configuration
influx_url = "http://127.0.0.1:8086"
influx_token = "secret-token"
influx_org = "InfluxData"
influx_bucket = "manufacturing"

# Initialize the InfluxDB Client with username and password
client_influx = InfluxDBClient(url=influx_url, token=influx_token, org=influx_org)

# Get the write API
write_api = client_influx.write_api(write_options=SYNCHRONOUS)

# Callback when the client receives a CONNACK response from the server
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    # Subscribe to both topics
    client.subscribe([(mqtt_topic1, 0), (mqtt_topic2, 0)])

# Callback for when a message is received from the server
def on_message(client, userdata, msg):
    #print(f"Message received `{msg.topic}`: {str(msg.payload)}")

    # Create a point and write it to InfluxDB
    #data = Point("measurement_name").tag("topic", msg.topic).field("value", float(msg.payload.decode('utf-8')))
    
    # Write the data to InfluxDB
    #write_api.write(bucket=influx_bucket, record=data)

    #def on_message(client, userdata, msg):
    print(f"Message received `{msg.topic}`: {msg.payload.decode('utf-8')}")

    # Parse the JSON data from the message payload
    json_data = json.loads(msg.payload.decode('utf-8'))
    data = json_data.get("data")

    if data:
        # Prepare a point with the measurement name, e.g., "production_data"
        # point = Point("production_data").time(data.get("Timestamp"), WritePrecision.NS)
        point = Point(msg.topic).time(data.get("Timestamp"), WritePrecision.NS)
        
        # Add tags and fields from the JSON data
        for key, value in data.items():
            if key not in ["Timestamp"]:  # Exclude the timestamp as it's already used for the point time
                # Assuming all other fields are not nested and can be directly added
                point = point.field(key, value)

        # Write the point to InfluxDB
        write_api.write(bucket=influx_bucket, record=point)

# Initialize MQTT Client
print("Initializing MQTT Client...")
print("MQTT Broker: ", mqtt_broker)
print("MQTT Port: ", mqtt_port)
print("MQTT Topic1: ", mqtt_topic1)
print("MQTT Topic2: ", mqtt_topic2)
print("InfluxDB URL: ", influx_url)
print("InfluxDB Token: ", influx_token)
print("InfluxDB Org: ", influx_org)
print("InfluxDB Bucket: ", influx_bucket)
print("Connecting to MQTT Broker...")

#client_mqtt = mqtt.Client()
# UPDATE DERIVATED POF NEW PAHO LIB
client_mqtt = f'python-mqtt-{random.randint(0, 1000)}'
#client1 = mqtt.Client(client_id1)  PAHO LIB - UPDATE FEB 2024
client_mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id1)

#client_mqtt = mqtt.Client()
    
    
client_mqtt.on_connect = on_connect
client_mqtt.on_message = on_message

# Connect to MQTT Broker
client_mqtt.connect(mqtt_broker, mqtt_port, 60)

# Process messages indefinitely
client_mqtt.loop_forever()
