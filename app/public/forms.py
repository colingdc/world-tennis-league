from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import InputRequired, Email, Length, Optional


class ContactForm(FlaskForm):
    email = StringField(
        "Email (si tu souhaites recevoir une réponse)",
        validators=[
            Optional(),
            Length(1, 64),
            Email()
        ]
    )
    message = TextAreaField(
        "Message *",
        validators=[
            InputRequired(),
            Length(max=1000)
        ]
    )
