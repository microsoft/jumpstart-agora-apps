FROM mcr.microsoft.com/cbl-mariner/base/python:3

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

COPY app/ .

EXPOSE 4840
CMD [ "python3",  "sim_server_controller.py", "/config/simulator.json" ]