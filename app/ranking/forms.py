from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import SelectField


class RankingForm(FlaskForm):
    week_name = SelectField(_l("week"), coerce=int)


class MonthlyRankingForm(FlaskForm):
    month_name = SelectField(_l("month"))
