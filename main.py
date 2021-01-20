from flask import Flask, render_template, request, jsonify
import os
from google.cloud import datastore


app = Flask(__name__)

datastore_client = datastore.Client('agile-team-299406')

@app.route('/')
def home():


    return render_template('mymap.html')

@app.route('/save', methods=['POST'])
def save_to_db():
    data = request.data.decode()
    kind = 'HiveLocation'
    name = 'beemap1'
    task_key = datastore_client.key('HiveLocation')
    task = datastore.Entity(key=task_key)
    task['location'] = data
    
    datastore_client.put(task)
    print (data)
    return (data)

@app.route('/delete', methods=['DELETE'])
def delete_from_db():
    data = request.data
    print (data)
    return (data)

@app.route('/update', methods=['GET'])
def load_db():
    query = datastore_client.query(kind='HiveLocation')
    query.order = ['location']
    a = list(query.fetch())



if __name__ == '__main__':
    host = os.getenv("HOST", "127.0.0.1")
    port = os.getenv("PORT", "5000")

    app.run(host=host, port=port)
