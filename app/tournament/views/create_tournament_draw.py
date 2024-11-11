from flask import redirect, render_template, request, url_for
from flask_babel import _

from .. import bp
from ..forms import CreateTournamentDrawForm
from ..lib import fetch_tournament
from ... import db
from ...decorators import manager_required
from ...models import Player, TournamentPlayer
from ...navigation import go_to_tournament_page
from ...notifications import display_info_message


@bp.route("/<tournament_id>/draw/create", methods=["GET", "POST"])
@manager_required
def create_tournament_draw(tournament_id):
    tournament = fetch_tournament(tournament_id)

    matches_with_tournament_player = [
        match for match in tournament.matches
        if match.tournament_player1_id or match.tournament_player2_id
    ]

    if len(matches_with_tournament_player) > 0:
        return redirect(url_for(".edit_tournament_draw", tournament_id=tournament_id))

    matches = tournament.get_matches_first_round()

    if not request.form:
        form = CreateTournamentDrawForm()

        for __ in matches:
            form.players.append_entry()

    else:
        form = CreateTournamentDrawForm(request.form)

    player_names = [(-1, _("choose_a_player"))] + Player.get_all()

    for player in form.players:
        player.player1_name.choices = player_names
        player.player2_name.choices = player_names

    if form.validate_on_submit():
        qualifier_count = 0
        for match, player in zip(matches, form.players):
            if player.data["player1_name"] >= 0:
                player_id = player.data["player1_name"]
                qualifier_id = None
            else:
                player_id = None
                qualifier_count += 1
                qualifier_id = qualifier_count

            tournament_player1 = TournamentPlayer(
                player_id=player_id,
                seed=player.data["player1_seed"],
                status=player.data["player1_status"],
                position=0,
                qualifier_id=qualifier_id,
                tournament_id=tournament_id
            )

            if player.data["player2_name"] >= 0:
                player_id = player.data["player2_name"]
                qualifier_id = None
            else:
                player_id = None
                qualifier_count += 1
                qualifier_id = qualifier_count

            tournament_player2 = TournamentPlayer(
                player_id=player_id,
                seed=player.data["player2_seed"],
                status=player.data["player2_status"],
                position=1,
                qualifier_id=qualifier_id,
                tournament_id=tournament_id
            )

            db.session.add(tournament_player1)
            db.session.add(tournament_player2)
            db.session.commit()

            match.tournament_player1_id = tournament_player1.id
            match.tournament_player2_id = tournament_player2.id
            db.session.add(match)
            db.session.commit()

        display_info_message(_("tournament_draw_created", tournament_name=tournament.name))
        return go_to_tournament_page(tournament_id)
    else:
        return render_template(
            "tournament/create_tournament_draw.html",
            title=_("tournament_draw", tournament_name=tournament.name),
            form=form,
            tournament=tournament
        )
