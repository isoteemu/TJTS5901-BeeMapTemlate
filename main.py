from flask import Flask, render_template
import os
from google.cloud import datastore

from flask_wtf import FlaskForm
from wtforms import StringField, FileField
from wtforms.validators import DataRequired
from wtforms.fields.html5 import EmailField
from flask_wtf.file import FileAllowed

app = Flask(__name__)
SECRET_KEY = os.urandom(32)
app.config["SECRET_KEY"] = SECRET_KEY
app.config["RECAPTCHA_PUBLIC_KEY"] = "6LeYIbsSAAAAACRPIllxA7wvXjIE411PfdB2gt2J"
app.config["RECAPTCHA_PRIVATE_KEY"] = "6LeYIbsSAAAAAJezaIq3Ft_hSTo0YtyeFG-JgRtu"

datastore_client = datastore.Client()


class MyForm(FlaskForm):
    firstname = StringField("firstname", validators=[DataRequired()])
    surname = StringField("surname", validators=[DataRequired()])
    # recaptcha = RecaptchaField()
    email = EmailField("email", validators=[DataRequired()])


@app.route("/")
def home():

    form = MyForm()
    locations = []
    for latlng in datastore_client.query(kind="HiveLocation").fetch():
        locations.append(
            {"lat": latlng["LatLng"].latitude, "lon": latlng["LatLng"].longitude}
        )

    return render_template("mymap.html", hive_locations=locations, form=form)


@app.route("/save", methods=["POST"])
def save_to_db():
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
