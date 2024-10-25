from datetime import date

from flask import redirect, render_template, url_for
from flask_babel import format_datetime

from .. import bp
from ..forms import MonthlyRankingForm
from ..lib import get_monthly_ranking
from ...decorators import login_required
from ...models import Tournament
from ...wordings import wordings


@bp.route("/monthly/", methods=["GET", "POST"])
@bp.route("/monthly/<year>/<month>", methods=["GET", "POST"])
@login_required
def monthly_ranking(year=None, month=None):
    form = MonthlyRankingForm()

    months = list(reversed(sorted(set((t.started_at.year, t.started_at.month) for t in Tournament.query))))

    def format_date(year, month):
        return format_datetime(date(int(year), int(month), 1), "MMMM yyyy").capitalize()

    form.month_name.choices = [("", wordings["choose_a_month"])] + [
        (f"{year}-{month}", format_date(year, month)) for year, month in months]

    if form.validate_on_submit() and form.month_name.data != "":
        year, month = form.month_name.data.split("-")
        return redirect(url_for(".monthly_ranking", year=int(year), month=int(month)))

    ranking = get_monthly_ranking(year, month) if year and month else None
    month_name = format_date(year, month) if year and month else None

    return render_template(
        "ranking/monthly.html",
        title=wordings["monthly_rankings"],
        month_name=month_name,
        form=form,
        ranking=ranking
    )
