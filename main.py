from flask import Flask, render_template, request, jsonify
import os
from google.cloud import datastore
import time
import uuid
import logging

# Set up the most basic logging.
logger = logging.getLogger(__name__)
logging.basicConfig()

app = Flask(__name__)

datastore_client = datastore.Client()

@app.route('/')
def home():

    locations = []
    for latlng in datastore_client.query(kind='HiveLocation').fetch():
        locations.append({
            "lat": latlng['LatLng'].latitude,
            "lon": latlng['LatLng'].longitude
        })

    return render_template('mymap.html', hive_locations=locations)


@app.route('/save', methods=['POST'])
def save_to_db():
    data = request.data.decode()


    kind = 'HiveLocation'
    name = uuid.uuid5("farts", "foo")
    task_key = datastore_client.key(kind, name)
    task = datastore.Entity(key=task_key)
    task['location'] = data
    task['bonus'] = 'something'

    datastore_client.put(task)


@app.route('/delete', methods=['DELETE'])
def delete_from_db():
    pass

@app.route('/update', methods=['GET'])
def load_db():
    query = datastore_client.query(kind='HiveLocation')
    query.order = ['location']
    data = list(query.fetch())
    print(data)



if __name__ == '__main__':

    host = os.getenv("HOST", "127.0.0.1")
    port = os.getenv("PORT", "5000")

    if app.config['DEBUG']:
        logger.setLevel(logging.DEBUG)

    logger.info(f"Starting {__name__} loop at {host}:{port}")

    app.run(host=host, port=port) or logger.warning(f"Flask app {__name__} failed!")
