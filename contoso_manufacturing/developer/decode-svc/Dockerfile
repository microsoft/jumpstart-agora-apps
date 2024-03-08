# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir opencv-python-headless requests

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV rtsp_url="rtsp://127.0.01:8554"
ENV save_path="./frames"
ENV inference_url="./frames"

# Run app.py when the container launches
CMD ["python", "app.py"]
