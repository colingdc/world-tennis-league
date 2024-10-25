from flask import redirect, render_template, request, url_for

from .. import bp
from ..forms import EditPlayerForm
from ... import db
from ...decorators import manager_required
from ...models import Player
from ...notifications import display_info_message


@bp.route("/<player_id>/edit", methods=["GET", "POST"])
@manager_required
def edit_player(player_id):
    player = Player.query.get_or_404(player_id)
    form = EditPlayerForm(request.form)

    if request.method == "GET":
        form.first_name.data = player.first_name
        form.last_name.data = player.last_name

    if form.validate_on_submit():
        player.first_name = form.first_name.data
        player.last_name = form.last_name.data

        db.session.add(player)
        db.session.commit()

        display_info_message(f"Le joueur {player.get_name()} a été mis à jour")
        return redirect(url_for(".view_players"))
    else:
        return render_template(
            "player/edit_player.html",
            title=player.get_name(),
            form=form,
            player=player
        )
