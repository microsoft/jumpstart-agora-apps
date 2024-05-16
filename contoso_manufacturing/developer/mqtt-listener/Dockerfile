# Use a base Python image
FROM python:3.8-slim

# Copy application files to the container
COPY . /app

# Set the working directory
WORKDIR /app

# Install dependencies
RUN pip install paho-mqtt
RUN pip install influxdb-client

# Set environment variables
ENV MQTT_BROKER="10.211.55.23"
ENV MQTT_PORT=1883
ENV MQTT_TOPIC1="topic/weldingrobot"
ENV MQTT_TOPIC2="topic/assemblybatteries"
ENV MQTT_TOPIC3="topic/assemblyline"
ENV INFLUX_URL="http://10.211.55.23:8086"
ENV INFLUX_TOKEN="secret-token"
ENV INFLUX_ORG="InfluxData"
ENV INFLUX_BUCKET="manufacturing"

# Command to run the application
CMD ["python", "mqtt-listener.py"]