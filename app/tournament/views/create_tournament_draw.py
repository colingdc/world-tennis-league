from flask import redirect, render_template, request, url_for

from .. import bp
from ..forms import CreateTournamentDrawForm
from ..lib import fetch_tournament
from ... import db
from ...decorators import manager_required
from ...models import Player, TournamentPlayer
from ...notifications import display_info_message


@bp.route("/<tournament_id>/draw/create", methods=["GET", "POST"])
@manager_required
def create_tournament_draw(tournament_id):
    tournament = fetch_tournament(tournament_id)

    matches_with_tournament_player = [m for m in tournament.matches
                                      if m.tournament_player1_id
                                      or m.tournament_player2_id]

    if len(matches_with_tournament_player) > 0:
        return redirect(url_for(".edit_tournament_draw", tournament_id=tournament_id))

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

            t1 = TournamentPlayer(
                player_id=player_id,
                seed=p.data["player1_seed"],
                status=p.data["player1_status"],
                position=0,
                qualifier_id=qualifier_id,
                tournament_id=tournament_id
            )

            if p.data["player2_name"] >= 0:
                player_id = p.data["player2_name"]
                qualifier_id = None
            else:
                player_id = None
                qualifier_count += 1
                qualifier_id = qualifier_count

            t2 = TournamentPlayer(
                player_id=player_id,
                seed=p.data["player2_seed"],
                status=p.data["player2_status"],
                position=1,
                qualifier_id=qualifier_id,
                tournament_id=tournament_id
            )

            # Add tournament players
            db.session.add(t1)
            db.session.add(t2)
            db.session.commit()

            # Link these tournament players to the match
            match.tournament_player1_id = t1.id
            match.tournament_player2_id = t2.id
            db.session.add(match)
            db.session.commit()

        display_info_message(f"Le tableau du tournoi {tournament.name} a été créé")
        return redirect(url_for(".view_tournament", tournament_id=tournament_id))
    else:
        return render_template(
            "tournament/create_tournament_draw.html",
            title=f"{tournament.name} – Tableau",
            form=form,
            tournament=tournament
        )
