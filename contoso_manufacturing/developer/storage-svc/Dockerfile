# Use an official Python base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file first to leverage Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the working directory in the container
COPY . .

# Expose the port the Flask app will listen on
EXPOSE 5000

ENV INFLUXDB_URL="http://10.211.55.23:8086"
ENV INFLUXDB_TOKEN=secret-token
ENV INFLUXDB_ORG=InfluxData
ENV INFLUXDB_BUCKET=manufacturing

# Command to run the Flask application
CMD ["flask", "run", "--host=0.0.0.0"]
