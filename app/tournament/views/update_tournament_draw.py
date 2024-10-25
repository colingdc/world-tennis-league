import json

from flask import redirect, render_template, url_for, abort

from .. import bp
from ..forms import FillTournamentDrawForm
from ..lib import fetch_tournament
from ... import db
from ...decorators import manager_required
from ...wordings import wordings


@bp.route("/<tournament_id>/draw/update", methods=["GET", "POST"])
@manager_required
def update_tournament_draw(tournament_id):
    tournament = fetch_tournament(tournament_id)

    if tournament.deleted_at:
        abort(404)

    form = FillTournamentDrawForm()

    if form.validate_on_submit():
        try:
            results = json.loads(form.forecast.data)
        except json.decoder.JSONDecodeError:
            return redirect(url_for(".view_tournament", tournament_id=tournament_id))

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
            return redirect(url_for(".close_tournament", tournament_id=tournament_id))

        return redirect(url_for(".view_tournament", tournament_id=tournament_id))

    else:
        return render_template(
            "tournament/update_tournament_draw.html",
            title=wordings["tournament_draw"].format(tournament.name),
            tournament=tournament,
            form=form
        )
