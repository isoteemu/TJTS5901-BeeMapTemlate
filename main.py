import logging
import os

from flask import Flask
from flask import Markup
from flask import render_template
from flask import request
from flask import Response
from flask_babel import Babel
from google.cloud import datastore
from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.ext.flask.flask_middleware import FlaskMiddleware
from opencensus.trace import execution_context
from opencensus.trace.samplers import ProbabilitySampler
from opencensus.trace.status import Status
from werkzeug.exceptions import HTTPException

# Set up the most basic logging.
logger = logging.getLogger(__name__)
logging.basicConfig()

logger = logging.getLogger(__name__)
app = Flask(__name__)
app.config.from_pyfile("default_config.py")
# silent param allows missing config files.
app.config.from_pyfile("instance_config.py", silent=True)

datastore_client = datastore.Client()

# Enable localization
Babel(app)


@app.route('/')
def home():

    locations = []

    # Setup custom tracer
    # Get the Tracer object
    tracer = execution_context.get_opencensus_tracer()
    # Name should be descriptive
    with tracer.span(name="datastore.query()") as span:

        kind = "Hive"
        locations = []
        for latlng in datastore_client.query(kind=kind).fetch():
            locations.append(
                {"lat": latlng["LatLng"]['latitude'], "lon": latlng["LatLng"]['longitude']}
            )

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


@app.route("/_divide_by_zero/<int:number>")
def division_by_zero(number: int):
    """Divide by zero. Should raise exception.
    Try requesting http://your-app/_divide_by_zero/7
    """
    result = -1
    try:
        result = number / 0
    except ZeroDivisionError:
        logger.exception("Failed to divide by zero", exc_info=True)
    return f"{number} divided by zeor is {result}"


def _setup_azure_logging(logger: logging.Logger, app: Flask, connection_string: str):
    """Setup logging into Azure Application Insights.

    :see: https://docs.microsoft.com/en-us/azure/azure-monitor/app/opencensus-python

    :param logger: Logging instance to a        ssign azure opencensus stream handler.
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


def capture_exceptions(app: Flask):
    """
    Register custom exception handler.

    When application falls short by unhandled exception, show custom error message.

    see: https://flask.palletsprojects.com/en/1.1.x/patterns/errorpages/
    """

    logger.debug("Setting up custom error handler")

    # Add handler for exception, and use decorator to register it.
    @app.errorhandler(Exception)
    def handle_internal_server_error(e):

        error_message = f"Server Error: {e!s}"

        # If fancy page fails, setup fallback
        error_page = Markup.escape(error_message)

        try:
            logger.exception(error_message, exc_info=e)

            # Collect routes
            routes = app.url_map.iter_rules()
            error_page = render_template("error.html", routes=routes, error=error_message)
        except Exception as e_in_e:
            # Nothing works and everything sucks.
            logger.error("Got `Exception` while handling another `Exception`.")
            logger.exception(e, exc_info=e_in_e)

        # Set default http code
        status = 500

        if isinstance(e, HTTPException):
            # HTTP exceptions have own error codes, so use it.
            status = e.code

        return Response(error_page, status=status)


# Setup logging into azure.
_app_insight_connection = app.config.get("APPLICATIONINSIGHTS_CONNECTION_STRING", False)

if _app_insight_connection:
    _setup_azure_logging(logger, app, _app_insight_connection)
else:
    logger.warn("Missing azure application insight key configuration value.")

# Register own error handler
capture_exceptions(app)

if __name__ == '__main__':

    host = os.getenv("HOST", "127.0.0.1")
    port = os.getenv("PORT", "5000")

    if app.config['DEBUG']:
        logger.setLevel(logging.DEBUG)

    logger.info(f"Starting {__name__} loop at {host}:{port}")

    app.run(host=host, port=port) or \
        logger.info(f"Abrupt Flask app stoppage")
