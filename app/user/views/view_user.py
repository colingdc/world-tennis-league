from flask import render_template
from flask_babel import _

from .. import bp
from ..lib import generate_chart
from ...decorators import login_required
from ...models import User
from ...wordings import wordings


@bp.route("/<user_id>")
@login_required
def view_user(user_id):
    user = User.query.get_or_404(user_id)

    rankings = generate_chart(user)

    series = [{"name": _("ranking"),
               "data": [{"x": int(t.started_at.strftime("%s")) * 1000,
                         "y": t.year_to_date_ranking or "null",
                         "tournament_name": t.name}
                        for t in rankings]}]

    return render_template(
        "main/view_user.html",
        title=wordings["profile_of"].format(user.username),
        series=series,
        user=user
    )
