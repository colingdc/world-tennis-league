from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired, Optional

from .lib import exists_by_name


class CreatePlayerForm(FlaskForm):
    first_name = StringField(
        _l("first_name"),
        validators=[
            Optional()
        ]
    )
    last_name = StringField(
        _l("last_name"),
        validators=[
            InputRequired(message=_l("mandatory_field"))
        ]
    )

    def validate(self):
        if not FlaskForm.validate(self):
            return False

        if exists_by_name(self.first_name.data, self.last_name.data):
            self.first_name.errors.append("")
            self.last_name.errors.append(_l("player_already_exists"))
            return False

        return True


class EditPlayerForm(FlaskForm):
    first_name = StringField(
        _l("first_name"),
        validators=[
            Optional()
        ]
    )
    last_name = StringField(
        _l("last_name"),
        validators=[
            InputRequired(message=_l("mandatory_field"))
        ]
    )

    def __init__(self, player, *args, **kwargs):
        super(EditPlayerForm, self).__init__(*args, **kwargs)
        self.player = player

    def validate(self):
        if not FlaskForm.validate(self):
            return False

        if ((self.first_name.data != self.player["first_name"]
             or self.last_name.data != self.player["last_name"])
                and exists_by_name(self.first_name.data, self.last_name.data)):
            self.first_name.errors.append("")
            self.last_name.errors.append(_l("player_already_exists"))
            return False

        return True
