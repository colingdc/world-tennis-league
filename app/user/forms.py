from flask_wtf import FlaskForm
from wtforms import BooleanField

from ..wordings import wordings


class SettingsForm(FlaskForm):
    notifications_activated = BooleanField(wordings["email_notifications_activated"])
