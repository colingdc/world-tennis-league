from flask import redirect, render_template, request, url_for
from flask_babel import _

from .. import bp
from ..forms import EditPlayerForm
from ..lib import fetch_player_by_id, update_player
from ...decorators import manager_required
from ...notifications import display_info_message


@bp.route("/<player_id>/edit", methods=["GET", "POST"])
@manager_required
def edit_player(player_id):
    player = fetch_player_by_id(player_id)
    form = EditPlayerForm(request.form)

    if request.method == "GET":
        form.first_name.data = player.first_name
        form.last_name.data = player.last_name

    if form.validate_on_submit():
        update_player(player, form.first_name.data, form.last_name.data)

        display_info_message(_("player_updated", player_name=player.get_name()))
        return redirect(url_for(".view_players"))
    else:
        return render_template(
            "player/edit_player.html",
            title=player.get_name(),
            form=form,
            player=player
        )
