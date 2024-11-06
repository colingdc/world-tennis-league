from .. import db
from ..models import User


def get_user_by_username(username):
    return User.query.filter_by(username=username).first()


def get_user_by_email(email):
    return User.query.filter_by(email=email).first()


def create_user(username, email, password):
    user = User(
        username=username,
        email=email,
        password=password,
        role_id=1
    )

    db.session.add(user)
    db.session.commit()

    return user
