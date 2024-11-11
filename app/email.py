from threading import Thread

from flask import current_app, render_template
from flask_mail import Message

from . import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()

    # Redirect all messages outside production to admin email account
    if not current_app.config.get("PRODUCTION"):
        to = current_app.config.get("ADMIN_WTL")

    message = Message(
        app.config["MAIL_SUBJECT_PREFIX"] + " " + subject,
        sender=app.config["MAIL_SENDER"],
        recipients=[to]
    )
    message.body = render_template(template + ".txt", **kwargs)
    message.html = render_template(template + ".html", **kwargs)
    thread = Thread(target=send_async_email, args=[app, message])
    thread.start()
    return thread
