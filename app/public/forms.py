from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import InputRequired, Email, Length, Optional


class ContactForm(FlaskForm):
    email = StringField(
        _l("email_if_answer_expected"),
        validators=[
            Optional(),
            Length(1, 64),
            Email()
        ]
    )
    message = TextAreaField(
        _l("message *"),
        validators=[
            InputRequired(),
            Length(max=1000)
        ]
    )
