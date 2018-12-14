import datetime
from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from . import db, bcrypt, login_manager


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    deleted_at = db.Column(db.DateTime, default=None)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    confirmed = db.Column(db.Boolean, default=False)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    participations = db.relationship(
        "Participation", backref="user", lazy="dynamic")

    def __repr__(self):
        return "<User %r>" % self.username

    def is_anonymous(self):
        return False

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password)

    def verify_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config["SECRET_KEY"], expiration)
        return s.dumps({"confirm": self.id})

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config["SECRET_KEY"], expiration)
        return s.dumps({"reset": self.id})

    def confirm(self, token):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token)
        except Exception as e:
            return False
        if data.get("confirm") != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token)
        except Exception as e:
            return False
        if data.get("reset") != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    @staticmethod
    def create_or_update(email, username, password, confirmed=True,
                         role_name="User"):
        role = Role.query.filter_by(name=role_name).first()
        if role is None:
            raise ValueError("This role does not exist")
        user = User.query.filter_by(email=email).first()
        email_exists = user is not None
        if not email_exists:
            user = User(email=email,
                        role=role,
                        confirmed=confirmed,
                        username=username,
                        password=password)
        try:
            db.session.add(user)
            db.session.commit()
            if email_exists:
                print(f"User {username} updated successfully")
            else:
                print(f"User {username} created successfully")
        except Exception as e:
            print(str(e))
            db.session.rollback()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def can(self, permissions):
        return (self.role is not None and
                (self.role.permissions & permissions) == permissions)

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def is_manager(self):
        return self.can(Permission.MANAGE_TOURNAMENT)

    def can_register_to_tournament(self, tournament):
        if not tournament.status == TournamentStatus.REGISTRATION_OPEN:
            return False
        start_date = tournament.week.start_date
        participations = (
            self.participations
            .join(Tournament)
            .join(TournamentWeek)
            .filter(TournamentWeek.start_date == start_date)
        )
        if participations.first():
            return False
        return True


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

    def is_manager(self):
        return False

    def is_anonymous(self):
        return True


login_manager.anonymous_user = AnonymousUser


class Permission:
    PARTICIPATE_TOURNAMENT = 0x01
    MANAGE_TOURNAMENT = 0x02
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship("User", backref="role", lazy="dynamic")

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.PARTICIPATE_TOURNAMENT, True),
            'Tournament Manager': (Permission.PARTICIPATE_TOURNAMENT |
                                   Permission.MANAGE_TOURNAMENT,
                                   False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return self.name


class TournamentWeek(db.Model):
    __tablename__ = "tournament_weeks"
    id = db.Column(db.Integer, primary_key=True)
    deleted_at = db.Column(db.DateTime, default=None)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    start_date = db.Column(db.Date)
    tournaments = db.relationship("Tournament", backref="week", lazy="dynamic")

    def get_name(self):
        year, week_number, _ = self.start_date.isocalendar()
        return f"{year} Semaine {week_number}"


class TournamentStatus:
    CREATED = 10
    REGISTRATION_OPEN = 20
    ONGOING = 30
    FINISHED = 40


class TournamentCategory:
    categories = {
        "Grand Chelem": [2000, 1200, 720, 360, 180, 90, 45, 10],
        "ATP 1000": [1000, 600, 360, 180, 90, 45, 25, 10],
        "ATP 500": [500, 300, 180, 90, 45, 20],
        "ATP 250": [250, 150, 90, 45, 20, 10],
    }


class Tournament(db.Model):
    __tablename__ = "tournaments"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    deleted_at = db.Column(db.DateTime, default=None)

    name = db.Column(db.String(64))
    started_at = db.Column(db.DateTime)
    number_rounds = db.Column(db.Integer)
    category = db.Column(db.String(64))
    status = db.Column(db.Integer, default=TournamentStatus.CREATED)
    week_id = db.Column(db.Integer, db.ForeignKey('tournament_weeks.id'))
    participations = db.relationship(
        "Participation", backref="tournament", lazy="dynamic")
    players = db.relationship(
        "TournamentPlayer", backref="tournament", lazy="dynamic")
    matches = db.relationship(
        "Match", backref="tournament", lazy="dynamic")

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def get_status(self):
        statuses = {
            10: "Créé",
            20: "Ouvert aux inscriptions",
            30: "En cours",
            40: "Terminé"
        }
        return statuses.get(self.status)

    def get_matches_first_round(self):
        return [m for m in self.matches if m.round == self.number_rounds]

    def is_draw_created(self):
        players = (TournamentPlayer.query
                   .filter(TournamentPlayer.tournament_id == self.id))
        return players.first() is not None


class Participation(db.Model):
    __tablename__ = "participations"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    deleted_at = db.Column(db.DateTime, default=None)
    round_reached = db.Column(db.Integer, default=0)
    points = db.Column(db.Integer, default=0)

    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class Player(db.Model):
    __tablename__ = "players"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    deleted_at = db.Column(db.DateTime, default=None)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    tournament_players = db.relationship(
        "TournamentPlayer", backref="player", lazy="dynamic")

    def get_name(self, format="full"):
        if format == "full":
            return f"{self.last_name.upper()}, {self.first_name}"

    @classmethod
    def get_all(cls, format="full"):
        return [(p.id, p.get_name(format))
                for p in cls.query.filter(cls.deleted_at.is_(None))
                .order_by(cls.last_name, cls.first_name).all()]


class TournamentPlayer(db.Model):
    __tablename__ = "tournament_players"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    deleted_at = db.Column(db.DateTime, default=None)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'))

    seed = db.Column(db.Integer)
    status = db.Column(db.String(8))
    qualifier_id = db.Column(db.Integer)
    position = db.Column(db.Integer)

    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.id'))
    matches = db.relationship(
        "Match",
        backref="tournament_player",
        primaryjoin="or_(TournamentPlayer.id==Match.tournament_player1_id, "
        "TournamentPlayer.id==Match.tournament_player2_id)",
        lazy='dynamic')


class Match(db.Model):
    __tablename__ = "matches"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    deleted_at = db.Column(db.DateTime)

    position = db.Column(db.Integer)
    round = db.Column(db.Integer)

    tournament_id = db.Column(
        db.Integer,
        db.ForeignKey('tournaments.id'))
    winner_id = db.Column(
        db.Integer,
        db.ForeignKey('tournament_players.id'))
    winner = db.relationship(
        "TournamentPlayer",
        foreign_keys="Match.winner_id")
    tournament_player1_id = db.Column(
        db.Integer,
        db.ForeignKey('tournament_players.id'))
    tournament_player2_id = db.Column(
        db.Integer,
        db.ForeignKey('tournament_players.id'))
    tournament_player1 = db.relationship(
        "TournamentPlayer",
        foreign_keys="Match.tournament_player1_id")
    tournament_player2 = db.relationship(
        "TournamentPlayer",
        foreign_keys="Match.tournament_player2_id")
