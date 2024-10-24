import json
from datetime import datetime, timedelta
from math import floor, log

from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user

from . import bp
from .forms import CreateTournamentDrawForm, CreateTournamentForm, EditTournamentForm, FillTournamentDrawForm, \
    MakeForecastForm
from .. import db
from ..constants import tournament_categories
from ..decorators import login_required, manager_required
from ..email import send_email
from ..models import Match, Participation, Player, Ranking, Tournament, TournamentPlayer, TournamentStatus, \
    TournamentWeek, User


@bp.route("/create", methods=["GET", "POST"])
@manager_required
def create_tournament():
    title = u"Créer un tournoi"
    form = CreateTournamentForm(request.form)
    form.category.choices = [("", "Choisir une catégorie")]
    form.category.choices += [(
        i, c["full_name"])
        for i, c in tournament_categories.items()]

    if form.validate_on_submit():
        monday = form.week.data - timedelta(days=form.week.data.weekday())
        tournament_week = (TournamentWeek.query
                           .filter_by(start_date=monday)
                           .first())
        if tournament_week is None:
            tournament_week = TournamentWeek(start_date=monday)
            db.session.add(tournament_week)
            db.session.commit()

        category = tournament_categories.get(form.category.data)
        number_rounds = category["number_rounds"]
        tournament = Tournament(name=form.name.data,
                                started_at=form.start_date.data,
                                week_id=tournament_week.id,
                                number_rounds=number_rounds,
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


@bp.route("/<tournament_id>/edit", methods=["GET", "POST"])
@manager_required
def edit_tournament(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    title = tournament.name
    form = EditTournamentForm(request.form)

    if request.method == "GET":
        form.name.data = tournament.name
        form.start_date.data = tournament.started_at
        form.week.data = tournament.week.start_date
    if form.validate_on_submit():
        monday = form.week.data - timedelta(days=form.week.data.weekday())
        tournament_week = (TournamentWeek.query
                           .filter_by(start_date=monday)
                           .first())
        if tournament_week is None:
            tournament_week = TournamentWeek(start_date=monday)
            db.session.add(tournament_week)
            db.session.commit()
        tournament.name = form.name.data
        tournament.started_at = form.start_date.data
        tournament.week = tournament_week
        db.session.add(tournament)
        db.session.commit()
        flash(f"Le tournoi {form.name.data} a été mis à jour", "info")
        return redirect(url_for(".edit_tournament",
                                tournament_id=tournament_id))
    else:
        return render_template("tournament/edit_tournament.html",
                               title=title,
                               form=form,
                               tournament=tournament)


@bp.route("/view")
@login_required
def view_tournaments():
    title = "Tournois"
    tournaments = (Tournament.query
                   .filter(Tournament.deleted_at.is_(None))
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
        participation = current_user.participation(tournament)
        form.player.choices = [(-1, "Choisir un joueur")]
        form.player.choices += [(p.id, p.get_name("last_name_first"))
                                for p in tournament.get_allowed_forecasts()]
        forbidden_forecasts = participation.get_forbidden_forecasts()
        forbidden_forecasts = ";".join([str(x) for x in forbidden_forecasts])
        if participation.tournament_player_id:
            form.player.data = participation.tournament_player_id
    else:
        form = None
        forbidden_forecasts = ""
    title = tournament.name
    return render_template("tournament/view_tournament.html",
                           title=title,
                           tournament=tournament,
                           form=form,
                           forbidden_forecasts=forbidden_forecasts)


@bp.route("/<tournament_id>/register")
@login_required
def register(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    if not current_user.can_register_to_tournament(tournament):
        flash("Tu n'es pas autorisé à t'inscrire à ce tournoi, soit "
              "doute car tu es déjà inscrit à un autre tournoi cette semaine,"
              "soit car les inscriptions sont fermées.",
              "warning")
        return redirect(url_for(".view_tournament",
                                tournament_id=tournament_id))

    participant = Participation(tournament_id=tournament_id,
                                user_id=current_user.id)
    db.session.add(participant)
    db.session.commit()
    flash(f"Tu es bien inscrit au tournoi {tournament.name}", "success")
    return redirect(url_for(".view_tournament", tournament_id=tournament_id))


@bp.route("/<tournament_id>/withdraw")
@login_required
def withdraw(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    if not current_user.participation(tournament):
        flash("Tu n'es pas inscrit à ce tournoi", "warning")
        return redirect(url_for(".view_tournament",
                                tournament_id=tournament_id))

    participation = current_user.participation(tournament)
    if not tournament.is_open_to_registration():
        flash("Tu ne peux plus te retirer de ce tournoi", "warning")
    else:
        participation.delete()
        flash(f"Tu es bien désinscrit du tournoi {tournament.name}", "success")
    return redirect(url_for(".view_tournament", tournament_id=tournament_id))


@bp.route("/<tournament_id>/draw/create", methods=["GET", "POST"])
@manager_required
def create_tournament_draw(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    title = f"{tournament.name} - Tableau"

    matches_with_tournament_player = [m for m in tournament.matches
                                      if m.tournament_player1_id
                                      or m.tournament_player2_id]

    if len(matches_with_tournament_player) > 0:
        return redirect(url_for(
            ".edit_tournament_draw", tournament_id=tournament_id))

    matches = tournament.get_matches_first_round()

    if not request.form:
        form = CreateTournamentDrawForm()

        for _ in matches:
            form.player.append_entry()

    else:
        form = CreateTournamentDrawForm(request.form)

    player_names = [(-1, "Choisir un joueur")] + Player.get_all()

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
    title = f"{tournament.name} - Tableau"

    matches = tournament.get_matches_first_round()
    participations = {p: p.tournament_player.player
                      for p in tournament.participations
                      if p.tournament_player}

    if not request.form:
        form = CreateTournamentDrawForm()

        for _ in matches:
            form.player.append_entry()

    else:
        form = CreateTournamentDrawForm(request.form)

    player_names = [(-1, "Choisir un joueur")] + Player.get_all()

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
        modified_players = []
        for match, p in zip(matches, form.player):
            if p.data["player1_name"] >= 0:
                player_id = p.data["player1_name"]
                qualifier_id = None
            else:
                player_id = None
                qualifier_count += 1
                qualifier_id = qualifier_count

            t1 = match.tournament_player1
            if t1.player_id != player_id:
                modified_players.append(t1.player)
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
            if t2.player_id != player_id:
                modified_players.append(t2.player)
            t2.player_id = player_id
            t2.seed = p.data["player2_seed"]
            t2.status = p.data["player2_status"]
            t2.qualifier_id = qualifier_id

            # Add tournament players
            db.session.add(t1)
            db.session.add(t2)
            db.session.commit()

        if tournament.is_open_to_registration():
            for participation, forecast in participations.items():
                if forecast in modified_players:
                    participation.tournament_player = None
                    send_email(
                        participation.user.email,
                        f"Tableau du tournoi {tournament.name} modifié",
                        "email/draw_updated",
                        user=participation.user,
                        tournament=tournament,
                        forecast=forecast)

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

    if int(request.form["player"]) == -1:
        forecast = None
        current_user.make_forecast(tournament, forecast)
        flash("Ton pronostic a bien été pris en compte.", "success")
        return redirect(url_for(".view_tournament",
                                tournament_id=tournament_id))

    forecast = int(request.form["player"])
    participation = current_user.participation(tournament)
    forbidden_forecasts = participation.get_forbidden_forecasts()
    allowed_forecasts = [x.id for x in tournament.get_allowed_forecasts()]

    if forecast in allowed_forecasts and forecast not in forbidden_forecasts:
        current_user.make_forecast(tournament, forecast)
        flash("Ton pronostic a bien été pris en compte.", "success")
    else:
        flash("Ce pronostic est invalide.", "warning")

    return redirect(url_for(".view_tournament",
                            tournament_id=tournament_id))


@bp.route("/<tournament_id>/draw")
@login_required
def view_tournament_draw(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    if tournament.deleted_at:
        abort(404)
    title = f"{tournament.name} - Tableau"

    return render_template("tournament/view_tournament_draw.html",
                           title=title,
                           tournament=tournament)


@bp.route("/<tournament_id>/draw/update", methods=["GET", "POST"])
@manager_required
def update_tournament_draw(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    if tournament.deleted_at:
        abort(404)
    title = f"Mettre à jour le tableau"

    form = FillTournamentDrawForm()

    if form.validate_on_submit():
        try:
            results = json.loads(form.forecast.data)
        except json.decoder.JSONDecodeError:
            return redirect(url_for(".view_tournament",
                                    tournament_id=tournament_id))

        matches = tournament.matches

        for match in matches:
            winner_id = results[str(match.id)]
            next_match = match.get_next_match()
            if winner_id == "None":
                match.winner_id = None
                if next_match:
                    if match.position % 2 == 0:
                        next_match.tournament_player1_id = None
                    else:
                        next_match.tournament_player2_id = None
                    db.session.add(next_match)
            else:
                match.winner_id = winner_id
                if next_match:
                    if match.position % 2 == 0:
                        next_match.tournament_player1_id = winner_id
                    else:
                        next_match.tournament_player2_id = winner_id
                    db.session.add(next_match)

            db.session.add(match)
        db.session.commit()

        tournament.compute_scores()

        if all(results[str(match.id)] != "None" for match in matches):
            return redirect(url_for(".close_tournament",
                                    tournament_id=tournament_id))

        return redirect(url_for(".view_tournament",
                                tournament_id=tournament_id))

    else:
        return render_template("tournament/update_tournament_draw.html",
                               title=title,
                               tournament=tournament,
                               form=form)


@bp.route("/<tournament_id>/open_registrations")
@manager_required
def open_registrations(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    tournament.status = TournamentStatus.REGISTRATION_OPEN
    db.session.add(tournament)
    db.session.commit()
    flash("Les inscriptions au tournoi sont ouvertes", "info")
    return redirect(url_for(".view_tournament",
                            tournament_id=tournament.id))


@bp.route("/<tournament_id>/close_registrations")
@manager_required
def close_registrations(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    tournament.status = TournamentStatus.ONGOING
    db.session.add(tournament)
    db.session.commit()

    for participant in tournament.participations:
        if not participant.has_made_forecast():
            db.session.delete(participant)
    db.session.commit()
    flash("Les inscriptions au tournoi sont closes", "info")
    return redirect(url_for(".view_tournament",
                            tournament_id=tournament.id))


@bp.route("/<tournament_id>/close_tournament")
@manager_required
def close_tournament(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)

    if tournament.status == TournamentStatus.FINISHED:
        return redirect(url_for(".view_tournament",
                                tournament_id=tournament.id))

    tournament.status = TournamentStatus.FINISHED
    db.session.add(tournament)
    db.session.commit()

    tournament.compute_scores()
    Ranking.compute_rankings(tournament.week)

    flash("Le tournoi a bien été clos", "info")
    return redirect(url_for(".view_tournament",
                            tournament_id=tournament.id))


@bp.route("/<tournament_id>/stats")
@login_required
def stats(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    return render_template("tournament/stats.html",
                           tournament=tournament)


@bp.route("/<tournament_id>/send_notification_email")
@manager_required
def send_notification_email(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)

    if all(t.notification_sent_at is not None for t in tournament.week.tournaments):
        flash("La notification par mail a déjà été envoyée pour tous les tournois de la semaine", "info")
        return redirect(url_for(".view_tournament",
                                tournament_id=tournament.id))

    for t in tournament.week.tournaments:
        t.notification_sent_at = datetime.now()
        db.session.add(t)
    db.session.commit()

    users_to_notify = User.query.filter(User.notifications_activated).filter(User.confirmed)

    for user in users_to_notify:
        send_email(
            user.email,
            f"Les tournois de la semaine sont ouverts aux inscriptions !",
            "email/registrations_open",
            user=user,
            tournaments=tournament.week.tournaments)

    flash("Les participants ont été notifiés par mail de l'ouverture des tournois de la semaine", "info")
    return redirect(url_for(".view_tournament",
                            tournament_id=tournament.id))
