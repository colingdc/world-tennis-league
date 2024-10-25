from flask import redirect, render_template, request, url_for

from .. import bp
from ..forms import CreatePlayerForm
from ..lib import insert_player
from ...decorators import manager_required
from ...notifications import display_info_message
from ...wordings import wordings


@bp.route("/create", methods=["GET", "POST"])
@manager_required
def create_player():
    form = CreatePlayerForm(request.form)

    if form.validate_on_submit():
        player = insert_player(form.first_name.data, form.last_name.data)

        display_info_message(wordings["player_created"].format(player.get_name()))
        return redirect(url_for(".create_player"))
    else:
        return render_template(
            "player/create_player.html",
            title="Créer un joueur",
            form=form
        )
