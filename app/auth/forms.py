from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class SignupForm(FlaskForm):
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Length(1, 64),
            Email()
        ]
    )
    password = PasswordField(
        'Mot de passe',
        validators=[
            DataRequired(),
            Length(min=8)
        ]
    )
    username = StringField(
        "Pseudo",
        validators=[
            DataRequired(),
            Length(1, 64)
        ]
    )
    submit = SubmitField("Valider")


class LoginForm(FlaskForm):
    username = StringField(
        "Pseudo",
        validators=[
            DataRequired()
        ]
    )
    password = PasswordField(
        "Mot de passe",
        validators=[
            DataRequired()
        ]
    )
    remember_me = BooleanField(
        "Se souvenir de moi",
        default=False
    )
    submit = SubmitField("Valider")


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(
        "Mot de passe actuel",
        validators=[
            DataRequired()
        ]
    )
    password = PasswordField(
        "Nouveau mot de passe",
        validators=[
            DataRequired(),
            Length(min=8),
            EqualTo('password2', message="Les mots de passe renseignés sont différents.")
        ]
    )
    password2 = PasswordField(
        "Confirmer le nouveau mot de passe",
        validators=[
            DataRequired()
        ]
    )
    submit = SubmitField("Valider")


class PasswordResetRequestForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Length(1, 64),
            Email()
        ]
    )
    submit = SubmitField("Valider")


class PasswordResetForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Length(1, 64),
            Email()
        ]
    )
    password = PasswordField(
        "Nouveau mot de passe",
        validators=[
            DataRequired(),
            Length(min=8),
            EqualTo('password2', message="Les mots de passe renseignés sont différents.")
        ]
    )
    password2 = PasswordField(
        "Confirmer le mot de passe",
        validators=[
            DataRequired()
        ]
    )
    submit = SubmitField("Valider")
