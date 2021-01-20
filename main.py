from flask import Flask, render_template, request, jsonify
import os
from google.cloud import datastore
import time

app = Flask(__name__)

datastore_client = datastore.Client('agile-team-299406')

@app.route('/')
def home():
    return render_template('mymap.html')

@app.route('/save', methods=['POST'])
def save_to_db():
    data = request.data.decode()
    kind = 'HiveLocation'
    name = time.strftime('%Y-%m-%d-%H:%M:%S')
    task_key = datastore_client.key(kind, name)
    task = datastore.Entity(key=task_key)
    task['location'] = data
    task['bonus'] = 'something'
    
    datastore_client.put(task)
    print (data)
    return (data)

@app.route('/delete', methods=['DELETE'])
def delete_from_db():
    pass

@app.route('/update', methods=['GET'])
def load_db():
    query = datastore_client.query(kind='HiveLocation')
    query.order = ['location']
    data = list(query.fetch())
    return data

if __name__ == '__main__':
    host = os.getenv("HOST", "127.0.0.1")
    port = os.getenv("PORT", "5000")

    app.run(host=host, port=port)
