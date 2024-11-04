from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import BooleanField


class SettingsForm(FlaskForm):
    notifications_activated = BooleanField(_l("email_notifications_activated"))
