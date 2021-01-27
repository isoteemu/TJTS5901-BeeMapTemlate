import os
import uuid

from flask import Flask
from flask import render_template
from flask import request
from google.cloud import datastore

app = Flask(__name__)

datastore_client = datastore.Client()


@app.route("/")
def home():

    locations = []
    for latlng in datastore_client.query(kind="HiveLocation").fetch():
        locations.append(
            {"lat": latlng["LatLng"].latitude, "lon": latlng["LatLng"].longitude}
        )

    return render_template("mymap.html", hive_locations=locations)


@app.route("/save", methods=["POST"])
def save_to_db():
    data = request.data.decode()

    kind = "HiveLocation"
    name = uuid.uuid5("farts", "foo")
    task_key = datastore_client.key(kind, name)
    task = datastore.Entity(key=task_key)
    task["location"] = data
    task["bonus"] = "something"

    datastore_client.put(task)


@app.route("/delete", methods=["DELETE"])
def delete_from_db():
    pass


@app.route("/update", methods=["GET"])
def load_db():
    query = datastore_client.query(kind="HiveLocation")
    query.order = ["location"]
    data = list(query.fetch())
    print(data)


if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = os.getenv("PORT", "5000")

    app.run(host=host, port=port)
