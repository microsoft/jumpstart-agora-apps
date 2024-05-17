# Use a base Python image
FROM python:3.8-slim

# Copy application files to the container
COPY . /app

# Set the working directory
WORKDIR /app

# Install dependencies
RUN pip install paho-mqtt


ENV MQTT_BROKER="10.211.55.5"
ENV MQTT_PORT=1883
ENV FRECUENCY=60

# Command to run the application
CMD ["python", "mqtt_simulator.py"]