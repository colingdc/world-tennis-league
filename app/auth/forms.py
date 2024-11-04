from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class SignupForm(FlaskForm):
    email = StringField(
        _l("email"),
        validators=[
            DataRequired(),
            Length(1, 64),
            Email()
        ]
    )
    password = PasswordField(
        _l("password"),
        validators=[
            DataRequired(),
            Length(min=8)
        ]
    )
    username = StringField(
        _l("username"),
        validators=[
            DataRequired(),
            Length(1, 64)
        ]
    )


class LoginForm(FlaskForm):
    username = StringField(
        _l("username"),
        validators=[
            DataRequired()
        ]
    )
    password = PasswordField(
        _l("password"),
        validators=[
            DataRequired()
        ]
    )
    remember_me = BooleanField(
        _l("remember_me"),
        default=False
    )


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(
        _l("current_password"),
        validators=[
            DataRequired()
        ]
    )
    password = PasswordField(
        _l("new_password"),
        validators=[
            DataRequired(),
            Length(min=8),
            EqualTo("password2", message=_l("passwords_are_different"))
        ]
    )
    password2 = PasswordField(
        _l("confirm_new_password"),
        validators=[
            DataRequired()
        ]
    )


class PasswordResetRequestForm(FlaskForm):
    email = StringField(
        _l("email"),
        validators=[
            DataRequired(),
            Length(1, 64),
            Email()
        ]
    )


class PasswordResetForm(FlaskForm):
    email = StringField(
        _l("email"),
        validators=[
            DataRequired(),
            Length(1, 64),
            Email()
        ]
    )
    password = PasswordField(
        _l("new_password"),
        validators=[
            DataRequired(),
            Length(min=8),
            EqualTo("password2", message=_l("passwords_are_different"))
        ]
    )
    password2 = PasswordField(
        _l("confirm_password"),
        validators=[
            DataRequired()
        ]
    )
