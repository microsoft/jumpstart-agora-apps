import paho.mqtt.client as mqtt
import time
import random

# MQTT broker details
broker_address = "localhost"  # Replace with your MQTT broker's address
broker_port = 1883  # MQTT broker port (default is 1883)

# MQTT topic to publish to
topic = "test/topic"  # Replace with the topic you want to publish to

# Create an MQTT client
client = mqtt.Client()

# Connect to the MQTT broker
client.connect(broker_address, broker_port)

while True:
    try:
        # Generate some sample data (you can replace this with your own data)
        temperature = random.uniform(20, 30)  # Simulated temperature value
        humidity = random.uniform(40, 60)     # Simulated humidity value

        # Create a JSON payload with the data
        payload = {
            "temperature": temperature,
            "humidity": humidity
        }

        # Publish the data to the MQTT broker
        client.publish(topic, payload=str(payload))

        print(f"Published: {payload}")

        # Wait for a while before publishing the next data (e.g., every 5 seconds)
        time.sleep(20)

    except KeyboardInterrupt:
        print("Exiting...")
        client.disconnect()
        break
