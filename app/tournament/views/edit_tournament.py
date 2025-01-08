from datetime import timedelta

from flask import redirect, render_template, request, url_for
from flask_babel import _

from .. import bp
from ..forms import EditTournamentForm
from ..lib import insert_tournament_week, fetch_tournament_week_by_start_date, fetch_tournament
from ... import db
from ...decorators import manager_required
from ...notifications import display_info_message


@bp.route("/<tournament_id>/edit", methods=["GET", "POST"])
@manager_required
def edit_tournament(tournament_id):
    tournament = fetch_tournament(tournament_id)
    form = EditTournamentForm(request.form)

    if request.method == "GET":
        form.name.data = tournament.name
        form.start_date.data = tournament.started_at
        form.week.data = tournament.week.start_date

    if form.validate_on_submit():
        monday = form.week.data - timedelta(days=form.week.data.weekday())
        tournament_week = fetch_tournament_week_by_start_date(monday)

        if tournament_week is None:
            insert_tournament_week(monday)

        tournament.name = form.name.data
        tournament.started_at = form.start_date.data
        tournament.week = tournament_week

        db.session.add(tournament)
        db.session.commit()

        display_info_message(_("tournament_updated", tournament_name=form.name.data))
        return redirect(url_for(".edit_tournament", tournament_id=tournament_id))
    else:
        return render_template(
            "tournament/edit_tournament.html",
            title=tournament.name,
            form=form,
            tournament=tournament
        )
