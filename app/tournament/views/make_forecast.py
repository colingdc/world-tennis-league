from flask import redirect, url_for, request
from flask_login import current_user

from .. import bp
from ..lib import fetch_tournament
from ...decorators import login_required
from ...notifications import display_warning_message, display_success_message


@bp.route("/<tournament_id>/forecast", methods=["POST"])
@login_required
def make_forecast(tournament_id):
    tournament = fetch_tournament(tournament_id)

    if not current_user.can_make_forecast(tournament):
        display_warning_message("Tu n'es pas autorisé à faire un pronostic pour ce tournoi")
        return redirect(url_for(".view_tournament", tournament_id=tournament_id))

    if not request.form["player"]:
        display_warning_message("Requête invalide")
        return redirect(url_for(".view_tournament", tournament_id=tournament_id))

    if int(request.form["player"]) == -1:
        forecast = None
        current_user.make_forecast(tournament, forecast)

        display_success_message("Ton pronostic a bien été pris en compte.")
        return redirect(url_for(".view_tournament", tournament_id=tournament_id))

    forecast = int(request.form["player"])
    participation = current_user.participation(tournament)
    forbidden_forecasts = participation.get_forbidden_forecasts()
    allowed_forecasts = [x.id for x in tournament.get_allowed_forecasts()]

    if forecast in allowed_forecasts and forecast not in forbidden_forecasts:
        current_user.make_forecast(tournament, forecast)
        display_success_message("Ton pronostic a bien été pris en compte.")
    else:
        display_warning_message("Ce pronostic est invalide.")

    return redirect(url_for(".view_tournament", tournament_id=tournament_id))
