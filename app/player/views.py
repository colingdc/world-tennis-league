from flask import redirect, render_template, request, url_for

from . import bp
from .forms import CreatePlayerForm, EditPlayerForm
from .. import db
from ..decorators import manager_required
from ..models import Player
from ..notifications import display_info_message, display_danger_message


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


@bp.route("/<player_id>/delete")
@manager_required
def delete_player(player_id):
    player = Player.query.get_or_404(player_id)

    if player.tournament_players.count() > 0:
        tournament = player.tournament_players.first().tournament

        display_danger_message("Ce joueur ne peut pas être supprimé car il apparait dans le "
              f"tableau d'au moins un tournoi ({tournament.name})")

        return redirect(url_for(".view_players"))

    player.delete()

    display_info_message(f"Le joueur {player.get_name()} a été supprimé")

    return redirect(url_for(".view_players"))


@bp.route("/<player_id>")
@manager_required
def view_player(player_id):
    player = Player.query.get_or_404(player_id)

    return render_template(
        "player/view_player.html",
        title=player.get_name(),
        player=player
    )


@bp.route("/view")
@manager_required
def view_players():
    players = Player.query.order_by(Player.last_name, Player.first_name)

    return render_template(
        "player/view_players.html",
        title="Joueurs",
        players=players
    )
