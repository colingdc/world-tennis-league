from flask_wtf import FlaskForm
from wtforms import DateTimeField, FieldList, FormField, IntegerField, SelectField, StringField, SubmitField
from wtforms.validators import InputRequired, Optional


class CreateTournamentForm(FlaskForm):
    name = StringField(
        'Nom',
        validators=[
            InputRequired(message="Ce champ est obligatoire")
        ]
    )
    category = SelectField(
        'Catégorie',
        validators=[
            InputRequired(message="Ce champ est obligatoire")
        ]
    )
    start_date = DateTimeField(
        'Date de début',
        format="%d/%m/%Y %H:%M",
        validators=[
            InputRequired(message="Ce champ est obligatoire")
        ]
    )
    week = DateTimeField(
        'Semaine',
        format="%d/%m/%Y",
        validators=[
            InputRequired(message="Ce champ est obligatoire")
        ]
    )
    submit = SubmitField("Valider")


class EditTournamentForm(FlaskForm):
    name = StringField(
        'Nom',
        validators=[
            InputRequired(message="Ce champ est obligatoire")
        ]
    )
    start_date = DateTimeField(
        'Date de début',
        format="%d/%m/%Y %H:%M",
        validators=[
            InputRequired(message="Ce champ est obligatoire")
        ]
    )
    week = DateTimeField(
        'Semaine',
        format="%d/%m/%Y",
        validators=[
            InputRequired(message="Ce champ est obligatoire")
        ]
    )
    submit = SubmitField("Valider")


class PlayerTournamentDrawForm(FlaskForm):
    player1_name = SelectField("Joueur", coerce=int)
    player2_name = SelectField("Joueur", coerce=int)
    player1_status = StringField("Statut")
    player2_status = StringField("Statut")
    player1_seed = IntegerField("Tête de série", validators=[Optional()])
    player2_seed = IntegerField("Tête de série", validators=[Optional()])


class CreateTournamentDrawForm(FlaskForm):
    player = FieldList(FormField(PlayerTournamentDrawForm))
    submit = SubmitField("Valider")


class MakeForecastForm(FlaskForm):
    player = SelectField("Mon pronostic", coerce=int)
    submit = SubmitField("Valider")


class FillTournamentDrawForm(FlaskForm):
    forecast = StringField("forecast")
    submit = SubmitField("Valider")
