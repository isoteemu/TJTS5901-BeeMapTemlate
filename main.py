import os

from flask import Flask
from flask import render_template
from flask import request
from google.cloud import datastore

app = Flask(__name__)
app.config.from_pyfile("default_config.py")
# silent param allows missing config files.
app.config.from_pyfile("instance_config.py", silent=True)

datastore_client = datastore.Client()


@app.route("/")
def home():

    locations = []
    for latlng in datastore_client.query(kind="Hive").fetch():
        locations.append(
            {"lat": latlng["LatLng"]['latitude'], "lon": latlng["LatLng"]['longitude']}
        )

    return render_template("mymap.html", hive_locations=locations)


@app.route("/save", methods=["GET","POST"])
def save_to_db():

    data = request.get_json()
    print("saved", data,"!")
    kind = "Hive"
    #name = data['firstname']
    task_key = datastore_client.key(kind)
    task = datastore.Entity(key=task_key)
    task["LatLng"] = {
                        "latitude": data["latitude"],
                         "longitude": data["longitude"]}
    task["Firstname"] = data['firstname']
    task["Familyname"] = data['familyname']
    task["email"] = data['email']

    datastore_client.put(task)
    return home()

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
