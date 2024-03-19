# Use an official Python runtime as a parent image
#FROM python:3.9-slim
FROM ultralytics/ultralytics:latest

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

#RUN mkdir /app/frames

# Install any needed packages specified in requirements.txt
#RUN pip install -r requirements.txt
RUN pip3 install Flask==3.0.2

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV rtsp_url="rtsp://10.211.55.5:8554/stream"
ENV save_path="frames"
#ENV inference_url="frames"

# Run app.py when the container launches
CMD ["python", "main.py"]
