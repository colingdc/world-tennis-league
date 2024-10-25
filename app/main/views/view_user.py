from flask import render_template

from .. import bp
from ..lib import generate_chart
from ...decorators import login_required
from ...models import User


@bp.route("/user/<user_id>")
@login_required
def view_user(user_id):
    user = User.query.get_or_404(user_id)

    rankings = generate_chart(user)

    series = [{"name": "Classement",
               "data": [{"x": int(t.started_at.strftime("%s")) * 1000,
                         "y": t.year_to_date_ranking or "null",
                         "tournament_name": t.name}
                        for t in rankings]}]

    return render_template(
        "main/view_user.html",
        title=f"Profil de {user.username}",
        series=series,
        user=user
    )
