from flask import redirect, url_for, request
from flask_login import current_user

from .. import bp
from ..lib import fetch_tournament
from ...decorators import login_required
from ...notifications import display_warning_message, display_success_message
from ...wordings import wordings


@bp.route("/<tournament_id>/forecast", methods=["POST"])
@login_required
def make_forecast(tournament_id):
    tournament = fetch_tournament(tournament_id)

    if not current_user.can_make_forecast(tournament):
        display_warning_message(wordings["not_allowed_to_make_a_forecast"])
        return redirect(url_for(".view_tournament", tournament_id=tournament_id))

    if not request.form["player"]:
        display_warning_message(wordings["invalid_request"])
        return redirect(url_for(".view_tournament", tournament_id=tournament_id))

    if int(request.form["player"]) == -1:
        forecast = None
        current_user.make_forecast(tournament, forecast)

        display_success_message(wordings["forecast_confirmed"])
        return redirect(url_for(".view_tournament", tournament_id=tournament_id))

    forecast = int(request.form["player"])
    participation = current_user.participation(tournament)
    forbidden_forecasts = participation.get_forbidden_forecasts()
    allowed_forecasts = [x.id for x in tournament.get_allowed_forecasts()]

    if forecast in allowed_forecasts and forecast not in forbidden_forecasts:
        current_user.make_forecast(tournament, forecast)
        display_success_message(wordings["forecast_confirmed"])
    else:
        display_warning_message(wordings["invalid_forecast"])

    return redirect(url_for(".view_tournament", tournament_id=tournament_id))
