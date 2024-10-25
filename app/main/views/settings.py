from flask import render_template, request
from flask_login import current_user

from .. import bp
from ..forms import SettingsForm
from ... import db
from ...decorators import login_required
from ...notifications import display_info_message


@bp.route("/user/settings", methods=["GET", "POST"])
@login_required
def settings():
    form = SettingsForm(request.form)

    if request.method == "GET":
        form.notifications_activated.data = current_user.notifications_activated

    if form.validate_on_submit():
        current_user.notifications_activated = form.notifications_activated.data
        db.session.add(current_user)
        db.session.commit()
        display_info_message(f"Tes préférences de notifications ont été mises à jour")

    return render_template(
        "main/settings.html",
        title="Paramètres",
        form=form,
        user=current_user
    )
