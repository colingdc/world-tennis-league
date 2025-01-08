from flask import current_app, redirect, render_template, url_for
from flask_babel import _
from flask_login import current_user

from .. import bp
from ..forms import ContactForm
from ...email import send_email
from ...notifications import display_success_message


@bp.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()

    if form.validate_on_submit():
        message = form.message.data

        if current_user and hasattr(current_user, "username"):
            sender = current_user.username
        else:
            sender = _("anonymous")

        send_email(
            to=current_app.config["ADMIN_WTL"],
            subject=_("new_message_from", sender=sender),
            template="email/contact",
            message=message,
            email=form.email.data,
            user=current_user
        )

        display_success_message(_("message_sent"))
        return redirect(url_for(".contact"))

    return render_template(
        "public/contact.html",
        title=_("contact"),
        form=form
    )
