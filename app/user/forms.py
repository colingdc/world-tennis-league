from flask_babel import _
from flask_wtf import FlaskForm
from wtforms import BooleanField


class SettingsForm(FlaskForm):
    notifications_activated = BooleanField(_("email_notifications_activated"))
