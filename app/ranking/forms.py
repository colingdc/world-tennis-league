from flask_wtf import FlaskForm
from wtforms import SelectField

from ..wordings import wordings


class RankingForm(FlaskForm):
    week_name = SelectField(wordings["week"], coerce=int)


class MonthlyRankingForm(FlaskForm):
    month_name = SelectField(wordings["month"])
