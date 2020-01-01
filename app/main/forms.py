from flask_wtf import FlaskForm
from wtforms import BooleanField, SubmitField


class SettingsForm(FlaskForm):
    notifications_activated = BooleanField("Notifications par mail activées")
    submit = SubmitField("Valider")
