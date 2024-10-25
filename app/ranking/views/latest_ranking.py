from flask import abort, redirect, url_for

from .. import bp
from ...decorators import login_required
from ...models import Tournament


@bp.route("/latest")
@login_required
def latest_ranking():
    week = Tournament.get_latest_finished_tournament().week

    if week.deleted_at:
        abort(404)

    return redirect(url_for(".weekly_ranking", tournament_week_id=week.id))
