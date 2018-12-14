from datetime import timedelta
from math import floor, log

from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required, current_user

from . import bp
from .. import db
from ..decorators import manager_required
from ..models import (Tournament, TournamentWeek, Participation,
                      Match, TournamentCategory, TournamentPlayer, Player)
from .forms import (CreateTournamentForm,
                    CreateTournamentDrawForm, MakeForecastForm)


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
    if current_user.can_make_forecast(tournament):
        form = MakeForecastForm()
        form.player.choices = [(p.id, p.player.get_name())
                               for p in tournament.players]
        p = current_user.participation(tournament)
        if p:
            form.player.data = p.tournament_player_id
    else:
        form = None
    title = tournament.name
    return render_template("tournament/view_tournament.html",
                           title=title,
                           tournament=tournament,
                           form=form)


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


@bp.route("/<tournament_id>/draw/create", methods=["GET", "POST"])
@manager_required
def create_tournament_draw(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    title = u"{} - Tableau".format(tournament.name)

    matches = tournament.get_matches_first_round()

    if not request.form:
        form = CreateTournamentDrawForm()

        for _ in matches:
            form.player.append_entry()

    else:
        form = CreateTournamentDrawForm(request.form)

    player_names = [(-1, "Choisir un joueur...")] + Player.get_all()

    for p in form.player:
        p.player1_name.choices = player_names
        p.player2_name.choices = player_names

    if form.validate_on_submit():
        qualifier_count = 0
        for match, p in zip(matches, form.player):
            if p.data["player1_name"] >= 0:
                player_id = p.data["player1_name"]
                qualifier_id = None
            else:
                player_id = None
                qualifier_count += 1
                qualifier_id = qualifier_count
            t1 = TournamentPlayer(player_id=player_id,
                                  seed=p.data["player1_seed"],
                                  status=p.data["player1_status"],
                                  position=0,
                                  qualifier_id=qualifier_id,
                                  tournament_id=tournament_id)
            if p.data["player2_name"] >= 0:
                player_id = p.data["player2_name"]
                qualifier_id = None
            else:
                player_id = None
                qualifier_count += 1
                qualifier_id = qualifier_count
            t2 = TournamentPlayer(player_id=player_id,
                                  seed=p.data["player2_seed"],
                                  status=p.data["player2_status"],
                                  position=1,
                                  qualifier_id=qualifier_id,
                                  tournament_id=tournament_id)

            # Add tournament players
            db.session.add(t1)
            db.session.add(t2)
            db.session.commit()

            # Link these tournament players to the match
            match.tournament_player1_id = t1.id
            match.tournament_player2_id = t2.id
            db.session.add(match)
            db.session.commit()

        flash(f"Le tableau du tournoi {tournament.name} a été créé", "info")
        return redirect(url_for(".view_tournament",
                                tournament_id=tournament_id))
    else:
        return render_template("tournament/create_tournament_draw.html",
                               title=title,
                               form=form,
                               tournament=tournament)


@bp.route("/<tournament_id>/draw/edit", methods=["GET", "POST"])
@manager_required
def edit_tournament_draw(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    title = u"{} - Tableau".format(tournament.name)

    matches = tournament.get_matches_first_round()

    if not request.form:
        form = CreateTournamentDrawForm()

        for _ in matches:
            form.player.append_entry()

    else:
        form = CreateTournamentDrawForm(request.form)

    player_names = [(-1, "Choisir un joueur...")] + Player.get_all()

    for p in form.player:
        p.player1_name.choices = player_names
        p.player2_name.choices = player_names

    if request.method == "GET":
        for p, match in zip(form.player, matches):
            if match.tournament_player1.player:
                p.player1_name.data = match.tournament_player1.player.id
            if match.tournament_player2.player:
                p.player2_name.data = match.tournament_player2.player.id
            p.player1_status.data = match.tournament_player1.status
            p.player2_status.data = match.tournament_player2.status
            p.player1_seed.data = match.tournament_player1.seed
            p.player2_seed.data = match.tournament_player2.seed

    if form.validate_on_submit():
        qualifier_count = 0
        for match, p in zip(matches, form.player):
            if p.data["player1_name"] >= 0:
                player_id = p.data["player1_name"]
                qualifier_id = None
            else:
                player_id = None
                qualifier_count += 1
                qualifier_id = qualifier_count

            t1 = match.tournament_player1
            t1.player_id = player_id
            t1.seed = p.data["player1_seed"]
            t1.status = p.data["player1_status"]
            t1.qualifier_id = qualifier_id

            if p.data["player2_name"] >= 0:
                player_id = p.data["player2_name"]
                qualifier_id = None
            else:
                player_id = None
                qualifier_count += 1
                qualifier_id = qualifier_count

            t2 = match.tournament_player2
            t2.player_id = player_id
            t2.seed = p.data["player2_seed"]
            t2.status = p.data["player2_status"]
            t2.qualifier_id = qualifier_id

            # Add tournament players
            db.session.add(t1)
            db.session.add(t2)
            db.session.commit()

        flash(f"Le tableau du tournoi {tournament.name} a été modifié", "info")
        return redirect(url_for(".view_tournament",
                                tournament_id=tournament_id))
    else:
        return render_template("tournament/edit_tournament_draw.html",
                               title=title,
                               form=form,
                               tournament=tournament)


@bp.route("/<tournament_id>/forecast", methods=["POST"])
@login_required
def make_forecast(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    if not current_user.can_make_forecast(tournament):
        flash("Tu n'es pas autorisé à faire un pronostic pour ce tournoi",
              "warning")
        return redirect(url_for(".view_tournament",
                                tournament_id=tournament_id))

    if not request.form["player"]:
        flash("Requête invalide", "warning")
        return redirect(url_for(".view_tournament",
                                tournament_id=tournament_id))

    current_user.make_forecast(tournament, int(request.form["player"]))
    flash("Ton pronostic a bien été pris en compte.", "success")
    return redirect(url_for(".view_tournament",
                            tournament_id=tournament_id))
