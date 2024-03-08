from flask import Flask, request, jsonify
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import os

# Initialize Flask app
app = Flask(__name__)

# InfluxDB settings (adjust these to your InfluxDB setup)
INFLUXDB_URL = os.environ.get("INFLUXDB_URL","http://localhost:8086")
INFLUXDB_TOKEN = os.environ.get("INFLUXDB_TOKEN","Your_InfluxDB_Token")
INFLUXDB_ORG = os.environ.get("INFLUXDB_ORG","your_org")
INFLUXDB_BUCKET = os.environ.get("INFLUXDB_BUCKET","your_bucket")

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
    app.run(debug=True)
