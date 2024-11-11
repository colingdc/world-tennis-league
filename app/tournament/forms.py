from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import DateTimeField, FieldList, FormField, IntegerField, SelectField, StringField
from wtforms.validators import InputRequired, Optional


class CreateTournamentForm(FlaskForm):
    name = StringField(
        _l("name"),
        validators=[
            InputRequired(message=_l("mandatory_field"))
        ]
    )
    category = SelectField(
        _l("category"),
        validators=[
            InputRequired(message=_l("mandatory_field"))
        ]
    )
    start_date = DateTimeField(
        _l("start_date"),
        format="%d/%m/%Y %H:%M",
        validators=[
            InputRequired(message=_l("mandatory_field"))
        ]
    )
    week = DateTimeField(
        _l("week"),
        format="%d/%m/%Y",
        validators=[
            InputRequired(message=_l("mandatory_field"))
        ]
    )


class EditTournamentForm(FlaskForm):
    name = StringField(
        _l("name"),
        validators=[
            InputRequired(message=_l("mandatory_field"))
        ]
    )
    start_date = DateTimeField(
        _l("start_date"),
        format="%d/%m/%Y %H:%M",
        validators=[
            InputRequired(message=_l("mandatory_field"))
        ]
    )
    week = DateTimeField(
        _l("week"),
        format="%d/%m/%Y",
        validators=[
            InputRequired(message=_l("mandatory_field"))
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
    players = FieldList(FormField(PlayerTournamentDrawForm))


class MakeForecastForm(FlaskForm):
    player = SelectField(coerce=int)


class FillTournamentDrawForm(FlaskForm):
    forecast = StringField()
