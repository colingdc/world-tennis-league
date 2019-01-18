from flask_wtf import FlaskForm
from wtforms import SelectField


class RankingForm(FlaskForm):
    week_name = SelectField("Semaine", coerce=int)
