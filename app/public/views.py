from flask import current_app, flash, redirect, render_template, url_for
from flask_login import current_user

from . import bp
from .forms import ContactForm
from ..email import send_email


@bp.route("/")
def index():
    return render_template("public/index.html")


@bp.route("/partners")
def partners():
    return render_template("public/partners.html")


@bp.route("/networks")
def networks():
    return render_template("public/networks.html")


@bp.route("/support")
def support():
    return render_template("public/support.html")


@bp.route("/contact", methods=['GET', 'POST'])
def contact():
    title = "Contact"
    form = ContactForm()
    if form.validate_on_submit():
        message = form.message.data
        if current_user and hasattr(current_user, "username"):
            sender = current_user.username
        else:
            sender = "Anonyme"
        send_email(to=current_app.config["ADMIN_WTL"],
                   subject="Nouveau message de la part de {}".format(sender),
                   template="email/contact",
                   message=message,
                   email=form.email.data,
                   user=current_user)
        flash(u"Ton message a bien été envoyé.", "success")
        return redirect(url_for(".contact"))

    return render_template("public/contact.html",
                           form=form,
                           title=title)
