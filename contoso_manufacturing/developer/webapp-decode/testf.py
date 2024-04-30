from flask import Flask
import json

app = Flask(__name__)

@app.route("/")
def helloworld():
    return "Hello world"

@app.route("/get_data")
def getdata():
    data = {
        "name": "My Name",
        "url": "My url"
    }
    return json.dumps(data)

if __name__ == "__main__":
    app.run()
    app.run(port=3000, debug=True)