from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired, Optional

from ..models import Player


class CreatePlayerForm(FlaskForm):
    first_name = StringField(
        "Prénom",
        validators=[
            Optional()
        ]
    )
    last_name = StringField(
        "Nom",
        validators=[
            InputRequired(message="Ce champ est obligatoire")
        ]
    )

    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False
        if (Player.query.filter_by(first_name=self.first_name.data)
                        .filter_by(last_name=self.last_name.data).first()):
            self.first_name.errors.append("")
            self.last_name.errors.append("Ce joueur existe déjà")
            return False
        return True


class EditPlayerForm(FlaskForm):
    first_name = StringField(
        "Prénom",
        validators=[
            Optional()
        ]
    )
    last_name = StringField(
        "Nom",
        validators=[
            InputRequired(message="Ce champ est obligatoire")
        ]
    )

    def __init__(self, player, *args, **kwargs):
        super(EditPlayerForm, self).__init__(*args, **kwargs)
        self.player = player

    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False
        if ((self.first_name.data != self.player["first_name"]
             or self.last_name.data != self.player["last_name"])
            and (Player.query.filter_by(first_name=self.first_name.data)
                             .filter_by(last_name=self.last_name.data)
                             .first())):
            self.first_name.errors.append("")
            self.last_name.errors.append("Ce joueur existe déjà")
            return False
        return True
