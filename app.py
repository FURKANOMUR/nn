from flask import Flask, jsonify
from modbus_reader import read_meter

app = Flask(__name__)

@app.route("/")
def home():
    return {"status": "ENTES Energy Platform running"}

@app.route("/meter/<int:slave_id>")
def meter(slave_id):
    data = read_meter(slave_id)
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
