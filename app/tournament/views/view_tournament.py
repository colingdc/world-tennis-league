from flask import render_template
from flask_babel import _
from flask_login import current_user

from .. import bp
from ..forms import MakeForecastForm
from ..lib import fetch_tournament
from ...decorators import login_required


@bp.route("/<tournament_id>/view")
@login_required
def view_tournament(tournament_id):
    tournament = fetch_tournament(tournament_id)

    if current_user.can_make_forecast(tournament):
        form = MakeForecastForm()

        participation = current_user.get_participation(tournament)

        form.player.choices = [(-1, _("choose_a_player"))]
        form.player.choices += [
            (tournament_player.id, tournament_player.get_reversed_name())
            for tournament_player in tournament.get_allowed_forecasts()
        ]

        forbidden_forecasts = participation.get_forbidden_forecasts()
        forbidden_forecasts = ";".join([str(forecast) for forecast in forbidden_forecasts])

        if participation.tournament_player_id:
            form.player.data = participation.tournament_player_id
    else:
        form = None
        forbidden_forecasts = ""

    return render_template(
        "tournament/view_tournament.html",
        title=tournament.name,
        tournament=tournament,
        form=form,
        forbidden_forecasts=forbidden_forecasts
    )
