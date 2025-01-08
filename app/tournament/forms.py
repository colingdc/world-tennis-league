from flask_wtf import FlaskForm
from wtforms import DateTimeField, FieldList, FormField, IntegerField, SelectField, StringField
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


class PlayerTournamentDrawForm(FlaskForm):
    player1_name = SelectField(coerce=int)
    player2_name = SelectField(coerce=int)
    player1_status = StringField()
    player2_status = StringField()
    player1_seed = IntegerField(validators=[Optional()])
    player2_seed = IntegerField(validators=[Optional()])


class CreateTournamentDrawForm(FlaskForm):
    player = FieldList(FormField(PlayerTournamentDrawForm))


class MakeForecastForm(FlaskForm):
    player = SelectField(coerce=int)


class FillTournamentDrawForm(FlaskForm):
    forecast = StringField()
