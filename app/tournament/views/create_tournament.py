from datetime import timedelta

from flask import redirect, render_template, request, url_for
from flask_babel import _

from .. import bp
from ..forms import CreateTournamentForm
from ..lib import insert_tournament_week, fetch_tournament_week_by_start_date, insert_tournament
from ...constants import tournament_categories
from ...decorators import manager_required
from ...notifications import display_info_message


@bp.route("/create", methods=["GET", "POST"])
@manager_required
def create_tournament():
    form = CreateTournamentForm(request.form)
    form.category.choices = [("", _("choose_a_category"))]
    form.category.choices += [(
        i, c["full_name"])
        for i, c in tournament_categories.items()]

    if form.validate_on_submit():
        monday = form.week.data - timedelta(days=form.week.data.weekday())
        tournament_week = fetch_tournament_week_by_start_date(monday)

        if tournament_week is None:
            insert_tournament_week(monday)

        insert_tournament(
            name=form.name.data,
            start_date=form.start_date.data,
            week_id=tournament_week.id,
            category_name=form.category.data,
        )

        display_info_message(_("tournament_created", tournament_name=form.name.data))
        return redirect(url_for(".create_tournament"))
    else:
        return render_template(
            "tournament/create_tournament.html",
            title=_("create_a_tournament"),
            form=form
        )
