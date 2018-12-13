from datetime import timedelta
from math import floor, log

from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required, current_user

from . import bp
from .. import db
from ..decorators import manager_required
from ..models import (Tournament, TournamentWeek,
                      Participation, Match, TournamentCategory)
from .forms import CreateTournamentForm


@bp.route("/create", methods=["GET", "POST"])
@manager_required
def create_tournament():
    title = u"Créer un tournoi"
    form = CreateTournamentForm(request.form)
    form.category.choices = [("", "Choisissez une catégorie")]
    form.category.choices += [(c, c) for c in TournamentCategory.categories]

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
                                number_rounds=form.number_rounds.data,
                                category=form.category.data,
                                )
        db.session.add(tournament)
        db.session.commit()
        for i in range(1, 2 ** tournament.number_rounds):
            match = Match(position=i,
                          tournament_id=tournament.id,
                          round=floor(log(i) / log(2)) + 1)
            db.session.add(match)
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


@bp.route("/<tournament_id>/view")
@login_required
def view_tournament(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    title = tournament.name
    return render_template("tournament/view_tournament.html",
                           title=title,
                           tournament=tournament)


@bp.route("/<tournament_id>/register")
@login_required
def register(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    if not current_user.can_register_to_tournament(tournament):
        flash("Tu n'es pas autorisé à t'inscrire à ce tournoi, sans "
              "doute car tu es déjà inscrit à un autre tournoi cette semaine.",
              "warning")
        return redirect(url_for(".view_tournament",
                                tournament_id=tournament_id))

    participant = Participation(tournament_id=tournament_id,
                                user_id=current_user.id)
    db.session.add(participant)
    db.session.commit()
    flash(f"Tu es bien inscrit au tournoi {tournament.name}", "success")
    return redirect(url_for(".view_tournament", tournament_id=tournament_id))
