from influxdb_client.client.write_api import SYNCHRONOUS
import paho.mqtt.client as mqtt
import json
from influxdb_client import InfluxDBClient, Point, WritePrecision
import random
import time
from datetime import datetime
from influxdb_client.client.exceptions import InfluxDBError
import os


mqtt_broker = os.environ.get("MQTT_BROKER", "")
mqtt_port = int(os.environ.get("MQTT_PORT", ""))
mqtt_topic1 = os.environ.get("MQTT_TOPIC1", "")
mqtt_topic2 = os.environ.get("MQTT_TOPIC2", "")
mqtt_topic3 = os.environ.get("MQTT_TOPIC3", "")

influx_url = os.environ.get("INFLUX_URL", "")
influx_token = os.environ.get("INFLUX_TOKEN", "")
influx_org = os.environ.get("INFLUX_ORG", "")
influx_bucket = os.environ.get("INFLUX_BUCKET", "")


# Initialize InfluxDB Client
client_influx = InfluxDBClient(url=influx_url, token=influx_token, org=influx_org)
write_api = client_influx.write_api(write_options=SYNCHRONOUS)

def flatten_json(y):
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out

# Callback when the client receives a CONNACK response from the server
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    # Subscribe to the topics
    client.subscribe([(mqtt_topic1, 0), (mqtt_topic2, 0), (mqtt_topic3, 0)])

def on_message(client, userdata, msg):
    #print(f"Message received `{msg.topic}`: {msg.payload.decode('utf-8')}")
    
    print(msg.topic)

    if msg.topic == "topic/assemblybatteries":
        json_data = json.loads(msg.payload.decode('utf-8'))
        data = json_data.get("data")
        timestamp = data.get("date_time", datetime.utcnow().isoformat())
        write_data_point("assembly_batteries", data, timestamp)

    elif msg.topic == "topic/weldingrobot":
        json_data = json.loads(msg.payload.decode('utf-8'))
        data = json_data.get("data")
        timestamp = data.get("date_time", datetime.utcnow().isoformat())
        write_data_point("weldingrobot", data, timestamp)

    elif  msg.topic == "topic/assemblyline":
        json_data = json.loads(msg.payload.decode('utf-8'))
        data = json_data.get("data")
        data_flatten = flatten_json(data)
        write_data_point("assemblyline", data_flatten, datetime.utcnow().isoformat())


    else:
        # Handle other topics
        pass


def write_data_point(measurement_name, data, timestamp):
    try:
        print("measurement_name: ", measurement_name)
        #print("data: ", data)
        
        point = Point(measurement_name).time(timestamp, WritePrecision.NS)
        for key, value in data.items():
            if isinstance(value, (dict, list)):  # Check if the value is still a dict or list
                print(f"Skipping key {key} because it contains a non-primitive type.")
                continue
            if value is None:  # Skip None values to prevent issues in writing
                print(f"Skipping key {key} because the value is None.")
                continue
            point = point.field(key, value)
        
        result = write_api.write(bucket=influx_bucket, record=point)
        if result:
            print("Write successful: "+ measurement_name)
        else:
            print("Write failed: "+ measurement_name)
            
    except InfluxDBError as e:
        print(f"Failed to write data to InfluxDB for measurement {measurement_name}. Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while writing data to InfluxDB for measurement {measurement_name}. Error: {e}")


def write_data_point2(measurement_name, data, timestamp):
    try:
        print("measurement_name: " + measurement_name)
        # Ensure the data can be printed as a string, even if it's a complex object.
        #print("data: " + str(data))
        #print("data: " + str(data))
        
        point = Point(measurement_name).time(timestamp, WritePrecision.NS)
        for key, value in data.items():
            #if key != "Timestamp":  # Exclude the timestamp
            point = point.field(key, value)
        write_api.write(bucket=influx_bucket, record=point)
    except InfluxDBError as e:
        print(f"Failed to write data to InfluxDB for measurement {measurement_name}. Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while writing data to InfluxDB for measurement {measurement_name}. Error: {e}")

def write_single_data_point(measurement_name, data, timestamp):
    try:
        print("measurement_name: " + measurement_name)
        # Ensure the data can be printed as a string, even if it's a complex object.
        print("data: " + str(data))
        
        point = Point(measurement_name).time(timestamp, WritePrecision.NS)
        point = point.field(measurement_name, data)
        write_api.write(bucket=influx_bucket, record=point)
    except InfluxDBError as e:
        print(f"Failed to write data to InfluxDB for measurement {measurement_name}. Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while writing data to InfluxDB for measurement {measurement_name}. Error: {e}")


def main():
    client_id = f'python-mqtt-{random.randint(0, 1000)}'
    client_mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id)

    client_mqtt.on_connect = on_connect
    client_mqtt.on_message = on_message

    print("Connecting to MQTT Broker...")
    client_mqtt.connect(mqtt_broker, mqtt_port, 60)

    # Use a while True loop with connection handling
    while True:
        try:
            client_mqtt.loop_start()
            time.sleep(1)
        except KeyboardInterrupt:
            print("Stopping MQTT client...")
            client_mqtt.loop_stop()
            client_mqtt.disconnect()
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
