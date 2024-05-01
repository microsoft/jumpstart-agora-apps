# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container to leverage Docker layer caching
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install Flask
RUN pip install opencv-python-headless==4.5.5.62
RUN pip install ovmsclient
RUN pip install tabulate
#RUN pip install torch

# Copy the rest of the application's code into the container
COPY . .

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable to specify the host for Flask
ENV FLASK_RUN_HOST=0.0.0.0

# Run the application when the container launches
#CMD ["flask", "run", "--host=0.0.0.0"]
CMD ["python", "app.py"]
