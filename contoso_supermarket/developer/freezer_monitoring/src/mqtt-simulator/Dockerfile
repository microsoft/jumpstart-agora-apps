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

ENTRYPOINT ["python3", "./mqtt-simulator/main.py"]

