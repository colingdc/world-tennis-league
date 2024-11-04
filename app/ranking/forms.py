from flask_babel import _
from flask_wtf import FlaskForm
from wtforms import SelectField


class RankingForm(FlaskForm):
    week_name = SelectField(_("week"), coerce=int)


class MonthlyRankingForm(FlaskForm):
    month_name = SelectField(_("month"))
