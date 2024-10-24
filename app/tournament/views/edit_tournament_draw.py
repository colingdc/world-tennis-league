from flask import redirect, render_template, request, url_for

from .. import bp
from ..forms import CreateTournamentDrawForm
from ... import db
from ...decorators import manager_required
from ...email import send_email
from ...models import Tournament, Player
from ...notifications import display_info_message


@bp.route("/<tournament_id>/draw/edit", methods=["GET", "POST"])
@manager_required
def edit_tournament_draw(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)

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
            if match.tournament_player1 and match.tournament_player1.player:
                p.player1_name.data = match.tournament_player1.player.id

            if match.tournament_player2 and match.tournament_player2.player:
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
                        forecast=forecast
                    )

        display_info_message(f"Le tableau du tournoi {tournament.name} a été modifié")
        return redirect(url_for(".view_tournament", tournament_id=tournament_id))
    else:
        return render_template(
            "tournament/edit_tournament_draw.html",
            title=f"{tournament.name} – Tableau",
            form=form,
            tournament=tournament
        )
