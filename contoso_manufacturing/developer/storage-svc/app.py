from flask import Flask, request, jsonify
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import argparse
import os

# Initialize Flask app
app = Flask(__name__)

# InfluxDB settings (adjust these to your InfluxDB setup)
INFLUXDB_URL = os.environ.get("INFLUXDB_URL","http://10.211.55.5:8086")
INFLUXDB_TOKEN = os.environ.get("INFLUXDB_TOKEN","secret-token")
INFLUXDB_ORG = os.environ.get("INFLUXDB_ORG","InfluxData")
INFLUXDB_BUCKET = os.environ.get("INFLUXDB_BUCKET","manufacturing")

# InfluxDB client setup
client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

@app.route('/data', methods=['POST'])
def post_data():
    """Endpoint to receive data and store it in InfluxDB."""
    data = request.json

    # Construct data point
    point = (
        Point("measurement_name")
        .tag("tag_key", "tag_value")
        .field("field_key", data['value'])
        .time(data['timestamp'], WritePrecision.NS)
    )

    # Write data to InfluxDB
    write_api.write(bucket=INFLUXDB_BUCKET, record=point)

    return jsonify({"message": "Data stored successfully"}), 200

if __name__ == '__main__':
    #app.run(host="localhost", port=8080, debug=True)
    # construct the argument parser and parse command line arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--ip", type=str, required=False, default='0.0.0.0',
        help="ip address of the device")
    ap.add_argument("-o", "--port", type=int, required=False, default=8081, 
        help="ephemeral port number of the server (1024 to 65535)")
    ap.add_argument("-f", "--frame-count", type=int, default=32,
        help="# of frames used to construct the background model")
    args = vars(ap.parse_args())
