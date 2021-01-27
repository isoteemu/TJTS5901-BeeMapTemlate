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
from opencensus.trace import execution_context
from opencensus.trace.status import Status

# Set up the most basic logging.
logger = logging.getLogger(__name__)
logging.basicConfig()

logger = logging.getLogger(__name__)
app = Flask(__name__)

datastore_client = datastore.Client()


@app.route('/')
def home():

    locations = []

    # Setup custom tracer
    # Get the Tracer object
    tracer = execution_context.get_opencensus_tracer()
    # Name should be descriptive
    with tracer.span(name="datastore.query()") as span:

        kind = "HiveLocation"
        for latlng in datastore_client.query(kind=kind).fetch():
            locations.append({
                "lat": latlng['LatLng'].latitude,
                "lon": latlng['LatLng'].longitude
            })

        location_count = len(locations)
        logger.debug("Found %d HiveLocation entries for map." % location_count)

        # Add info into our trace
        # Annotation: https://opencensus.io/tracing/span/time_events/annotation/
        # Status: https://opencensus.io/tracing/span/status/

        # For annotation first param is description, additional are freeform attributes
        span.add_annotation("Query all hive locations from datastore", kind=kind, count=location_count)

        if location_count > 0:
            span.status = Status(0, "Found %d hive locations." % location_count)
        else:
            # Not found
            span.status = Status(5, "Zero locations found.")

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
    raise RuntimeError("Missing azure application insight key configuration value.")


if __name__ == '__main__':

    host = os.getenv("HOST", "127.0.0.1")
    port = os.getenv("PORT", "5000")

    if app.config['DEBUG']:
        logger.setLevel(logging.DEBUG)

    logger.info(f"Starting {__name__} loop at {host}:{port}")

    app.run(host=host, port=port) or \
        logger.info(f"Abrupt Flask app stoppage")

