FROM openvino/ubuntu20_runtime

USER root

RUN apt update
RUN apt install libopencv-dev python3-opencv -y

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
WORKDIR /tmp/opencl
RUN mkdir videos
RUN curl https://jumpstartprodsg.blob.core.windows.net/video/agora/supermarket.mp4 --output ./videos/supermarket.mp4
COPY . .

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=8000"]