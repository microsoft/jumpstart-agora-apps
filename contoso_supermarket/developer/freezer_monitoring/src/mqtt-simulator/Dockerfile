FROM ubuntu:latest

RUN apt update && apt install -y 
RUN apt install -y  git \
    python3 \
    nano

RUN apt install -y python3-pip
RUN apt install -y python3-venv

RUN pip3 install paho-mqtt==1.5.0

ARG PROJECT_NAME=vs
ARG PROJECT_ROOT=workspace

COPY ./config ./config
COPY ./mqtt-simulator ./mqtt-simulator

CMD ["python3", "./mqtt-simulator/main.py"]

###############################################################
# DOCKER BUILD COMMANDS
# docker build -t js/mqtt-simulator . ; ./Dockerrun.ps1
# docker build --progress=plain -t js/mqtt-simulator .
# docker build --progress=plain --no-cache -t js/mqtt-simulator .

# DOCKER RUN COMMAND
# docker run argument examples
# docker run 
# --hostname=my_test_machine 
# --mac-address makes dhcp assignment much easier!
# --mac-address=02:42:ac:11:00:03 
