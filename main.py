""" Apps backend """
import os

from flask import Flask
from flask import render_template
from flask_wtf import FlaskForm
from google.cloud import datastore
from wtforms import StringField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired

app = Flask(__name__)
SECRET_KEY = os.urandom(32)
app.config["SECRET_KEY"] = SECRET_KEY
app.config["RECAPTCHA_PUBLIC_KEY"] = "6LeYIbsSAAAAACRPIllxA7wvXjIE411PfdB2gt2J"
app.config["RECAPTCHA_PRIVATE_KEY"] = "6LeYIbsSAAAAAJezaIq3Ft_hSTo0YtyeFG-JgRtu"

datastore_client = datastore.Client()


class MyForm(FlaskForm):
    """ Form  to save the added location"""

    firstname = StringField("firstname", validators=[DataRequired()])
    surname = StringField("surname", validators=[DataRequired()])
    # recaptcha = RecaptchaField()
    email = EmailField("email", validators=[DataRequired()])


@app.route("/")
def home():
    """ Apps home page """
    form = MyForm()
    locations = []
    for latlng in datastore_client.query(kind="HiveLocation").fetch():
        locations.append(
            {"lat": latlng["LatLng"].latitude, "lon": latlng["LatLng"].longitude}
        )

    return render_template("mymap.html", hive_locations=locations, form=form)


@app.route("/save", methods=["POST"])
def save_to_db():
    """ Saving the form """
    form = MyForm()
    if form.validate_on_submit():
        firstname = form.firstname.data
        surname = form.surname.data
        email = form.email.data
        name = firstname + surname
        kind = "Email"
        task_key = datastore_client.key(kind, name)
        task = datastore.Entity(key=task_key)
        task["Email"] = email

        datastore_client.put(task)
    return home()


@app.route("/delete", methods=["DELETE"])
def delete_from_db():
    """ method to delete entries from database """


@app.route("/update", methods=["GET"])
def load_db():
    """ method to lead entries from database (UNUSED) """
    query = datastore_client.query(kind="HiveLocation")
    query.order = ["location"]
    data = list(query.fetch())
    print(data)


if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = os.getenv("PORT", "5000")

    app.run(host=host, port=port)
