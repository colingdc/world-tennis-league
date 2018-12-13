from datetime import timedelta

from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required

from . import bp
from .. import db
from ..decorators import manager_required
from ..models import Tournament, TournamentWeek
from .forms import CreateTournamentForm


@bp.route("/create", methods=["GET", "POST"])
@manager_required
def create_tournament():
    title = u"Créer un tournoi"
    form = CreateTournamentForm(request.form)

    if form.validate_on_submit():
        monday = form.week.data - timedelta(days=form.week.data.weekday())
        tournament_week = (TournamentWeek.query
                           .filter_by(start_date=monday)
                           .first())
        if tournament_week is None:
            tournament_week = TournamentWeek(start_date=monday)
            db.session.add(tournament_week)
            db.session.commit()
        tournament = Tournament(name=form.name.data,
                                started_at=form.start_date.data,
                                week_id=tournament_week.id,
                                )
        db.session.add(tournament)
        db.session.commit()
        flash(f"Le tournoi {form.name.data} a été créé", "info")
        return redirect(url_for(".create_tournament"))
    else:
        return render_template("tournament/create_tournament.html",
                               title=title,
                               form=form)


@bp.route("/view")
@login_required
def view_tournaments():
    title = "Tournois"
    tournaments = (Tournament.query
                   .filter(Tournament.deleted_at.is_(None))
                   .order_by(Tournament.started_at.desc())
                   )
    return render_template("tournament/view_tournaments.html",
                           title=title,
                           tournaments=tournaments)
