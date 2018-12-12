from flask_wtf import FlaskForm
from wtforms import DateTimeField, StringField, SubmitField
from wtforms.validators import InputRequired


class CreateTournamentForm(FlaskForm):
    name = StringField('Nom',
                       validators=[InputRequired(
                           message="Ce champ est obligatoire")])
    start_date = DateTimeField('Date de début',
                               format="%d/%m/%Y %H:%M",
                               validators=[InputRequired(
                                   message="Ce champ est obligatoire")])
    week = DateTimeField('Semaine',
                         format="%d/%m/%Y",
                         validators=[InputRequired(
                             message="Ce champ est obligatoire")])
    submit = SubmitField("Valider")
