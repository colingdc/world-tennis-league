from flask import redirect, render_template, request, url_for

from .. import bp
from ..forms import CreatePlayerForm
from ... import db
from ...decorators import manager_required
from ...models import Player
from ...notifications import display_info_message


@bp.route("/create", methods=["GET", "POST"])
@manager_required
def create_player():
    form = CreatePlayerForm(request.form)

    if form.validate_on_submit():
        player = Player(
            first_name=form.first_name.data,
            last_name=form.last_name.data
        )

        db.session.add(player)
        db.session.commit()

        display_info_message(f"Le joueur {player.get_name()} a été créé")
        return redirect(url_for(".create_player"))
    else:
        return render_template(
            "player/create_player.html",
            title="Créer un joueur",
            form=form
        )
