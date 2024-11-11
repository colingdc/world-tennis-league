from flask import render_template, request
from flask_babel import _

from .. import bp
from ..forms import CreateTournamentDrawForm
from ..lib import fetch_tournament
from ... import db
from ...decorators import manager_required
from ...email import send_email
from ...models import Player
from ...navigation import go_to_tournament_page
from ...notifications import display_info_message


@bp.route("/<tournament_id>/draw/edit", methods=["GET", "POST"])
@manager_required
def edit_tournament_draw(tournament_id):
    tournament = fetch_tournament(tournament_id)

    matches = tournament.get_matches_first_round()
    participations = {
        participation: participation.tournament_player.player
        for participation in tournament.participations
        if participation.tournament_player
    }

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

    if request.method == "GET":
        for player, match in zip(form.players, matches):
            if match.tournament_player1 and match.tournament_player1.player:
                player.player1_name.data = match.tournament_player1.player.id

            if match.tournament_player2 and match.tournament_player2.player:
                player.player2_name.data = match.tournament_player2.player.id

            player.player1_status.data = match.tournament_player1.status
            player.player2_status.data = match.tournament_player2.status
            player.player1_seed.data = match.tournament_player1.seed
            player.player2_seed.data = match.tournament_player2.seed

    if form.validate_on_submit():
        qualifier_count = 0
        modified_players = []
        for match, player in zip(matches, form.players):
            if player.data["player1_name"] >= 0:
                player_id = player.data["player1_name"]
                qualifier_id = None
            else:
                player_id = None
                qualifier_count += 1
                qualifier_id = qualifier_count

            tournament_player1 = match.tournament_player1
            if tournament_player1.player_id != player_id:
                modified_players.append(tournament_player1.player)
            tournament_player1.player_id = player_id
            tournament_player1.seed = player.data["player1_seed"]
            tournament_player1.status = player.data["player1_status"]
            tournament_player1.qualifier_id = qualifier_id

            if player.data["player2_name"] >= 0:
                player_id = player.data["player2_name"]
                qualifier_id = None
            else:
                player_id = None
                qualifier_count += 1
                qualifier_id = qualifier_count

            tournament_player2 = match.tournament_player2
            if tournament_player2.player_id != player_id:
                modified_players.append(tournament_player2.player)
            tournament_player2.player_id = player_id
            tournament_player2.seed = player.data["player2_seed"]
            tournament_player2.status = player.data["player2_status"]
            tournament_player2.qualifier_id = qualifier_id

            db.session.add(tournament_player1)
            db.session.add(tournament_player2)
            db.session.commit()

        if tournament.is_open_to_registration():
            for participation, forecast in participations.items():
                if forecast in modified_players:
                    participation.tournament_player = None

                    send_email(
                        participation.user.email,
                        _("tournament_draw_has_been_modified", tournament_name=tournament.name),
                        "email/draw_updated",
                        user=participation.user,
                        tournament=tournament,
                        forecast=forecast
                    )

        display_info_message(_("tournament_draw_updated", tournament_name=tournament.name))
        return go_to_tournament_page(tournament_id)
    else:
        return render_template(
            "tournament/edit_tournament_draw.html",
            title=_("tournament_draw", tournament_name=tournament.name),
            form=form,
            tournament=tournament
        )
