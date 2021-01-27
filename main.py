from flask import Flask, render_template, request, jsonify
import os
from google.cloud import datastore
import time
import uuid
import logging

from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.ext.flask.flask_middleware import FlaskMiddleware
from opencensus.trace.samplers import ProbabilitySampler

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

    logger.debug("Found %d HiveLocation entries for map." % len(locations))

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


def _setup_azure_logging(logger: logging.Logger, app: Flask, connection_string: str):
    """Setup logging into Azure Application Insights.

    :see: https://docs.microsoft.com/en-us/azure/azure-monitor/app/opencensus-python

    :param logger: Logging instance to assign azure opencensus stream handler.
    :param app: Flask app instance to assing azure opencensus handler.
    :param connection_string: Azure Application Insight connection string.
    """

    # Setup trace handler. Handles normal logging output:
    # >>> logger.info("Info message")
    azure_handler = AzureLogHandler(
        connection_string=connection_string
    )
    logger.addHandler(azure_handler)

    # Setup flask middleware, so pageview metrics are stored in azure.
    FlaskMiddleware(
        app,
        exporter=AzureExporter(connection_string=connection_string),
        sampler=ProbabilitySampler(rate=1.0),
    )


# Setup logging into azure.
_app_insight_connection = app.config.get("APPLICATIONINSIGHTS_CONNECTION_STRING", "InstrumentationKey=8290acaa-c1f8-4b32-862a-543608df5871;IngestionEndpoint=https://northeurope-0.in.applicationinsights.azure.com/")

if _app_insight_connection:
    _setup_azure_logging(logger, app, _app_insight_connection)
else:
    logger.warn("Missing azure application insight key. Logging to azure disabled.")


if __name__ == '__main__':

    host = os.getenv("HOST", "127.0.0.1")
    port = os.getenv("PORT", "5000")

    if app.config['DEBUG']:
        logger.setLevel(logging.DEBUG)

    logger.info(f"Starting {__name__} loop at {host}:{port}")

    app.run(host=host, port=port) or \
        logger.info(f"Abrupt Flask app stoppage")

