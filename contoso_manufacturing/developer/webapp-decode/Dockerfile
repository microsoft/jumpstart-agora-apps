# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Add depencecies
RUN apt update
RUN apt install libgtk2.0-dev pkg-config libgl1 -y

# Copy the requirements file into the container to leverage Docker layer caching
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code into the container
COPY . .

# Exlucde user config files
RUN rm -rf config/*

# Make port 5000 available to the world outside this container
EXPOSE 5001

# Run the application when the container launches
CMD ["python", "app.py"]