from flask import redirect, render_template, request, url_for
from flask_babel import _

from .. import bp
from ..forms import CreatePlayerForm
from ..lib import insert_player
from ...decorators import manager_required
from ...notifications import display_info_message


@bp.route("/create", methods=["GET", "POST"])
@manager_required
def create_player():
    form = CreatePlayerForm(request.form)

    if form.validate_on_submit():
        player = insert_player(form.first_name.data, form.last_name.data)

        display_info_message(_("player_created", player_name=player.get_standard_name()))
        return redirect(url_for(".create_player"))
    else:
        return render_template(
            "player/create_player.html",
            title=_("create_a_player"),
            form=form
        )
