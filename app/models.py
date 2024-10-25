import datetime

from flask import current_app
from flask_login import AnonymousUserMixin, UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from sqlalchemy import func

from . import bcrypt, db, login_manager
from .constants import tournament_categories


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    deleted_at = db.Column(db.DateTime, default=None)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    confirmed = db.Column(db.Boolean, default=False)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True)
    password_hash = db.Column(db.String(128))
    notifications_activated = db.Column(db.Boolean, default=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    participations = db.relationship("Participation", backref="user", lazy="dynamic")
    rankings = db.relationship("Ranking", backref="user", lazy="dynamic")

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
        self.notifications_activated = True
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
    def create_or_update(email, username, password, confirmed=True, role_name="User"):
        role = Role.query.filter_by(name=role_name).first()
        if role is None:
            raise ValueError("This role does not exist")
        user = User.query.filter_by(email=email).first()
        email_exists = user is not None
        if not email_exists:
            user = User(
                email=email,
                role=role,
                confirmed=confirmed,
                username=username,
                password=password
            )
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
        if self.role is None:
            return False

        return (self.role.permissions & permissions) == permissions

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
        return participations.first() is None

    def is_registered_to_other_tournament(self, tournament):
        start_date = tournament.week.start_date
        participations = (
            self.participations
                .join(Tournament)
                .join(TournamentWeek)
                .filter(TournamentWeek.start_date == start_date)
                .filter(Tournament.id != tournament.id)
        )
        return participations.first() or False

    def is_registered_to_tournament(self, tournament):
        return self.participation(tournament) is not None

    def can_make_forecast(self, tournament):
        return (
                tournament.status == TournamentStatus.REGISTRATION_OPEN
                and self.is_registered_to_tournament(tournament)
        )

    def participation(self, tournament):
        return (
            self.participations
                .join(Tournament)
                .filter(Tournament.id == tournament.id).first()
        )

    def make_forecast(self, tournament, tournament_player_id):
        participation = self.participation(tournament)
        participation.tournament_player_id = tournament_player_id
        db.session.add(self)
        db.session.commit()

    def get_participations(self):
        return (
            self.participations
                .filter(Participation.tournament_id.isnot(None))
                .join(Tournament)
                .order_by(Tournament.started_at.desc())
        )

    def get_current_ranking(self):
        return (
            Ranking.query
                .filter(Ranking.user_id == self.id)
                .order_by(Ranking.tournament_week_id.desc())
                .first()
        )


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
    rankings = db.relationship("Ranking", backref="week", lazy="dynamic")

    def get_name(self, format="long"):
        year, week_number, _ = self.start_date.isocalendar()
        if format == "long":
            name = f"{week_number} {year} - "
            name += ", ".join([t.name for t in self.tournaments])
            return name
        if format == "ranking":
            name = f"Semaine {week_number} {year} - "
            name += ", ".join([t.name for t in self.tournaments])
            return name
        return f"{year} Semaine {week_number}"


class TournamentStatus:
    CREATED = 10
    REGISTRATION_OPEN = 20
    ONGOING = 30
    FINISHED = 40


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
    notification_sent_at = db.Column(db.DateTime)

    week_id = db.Column(db.Integer, db.ForeignKey('tournament_weeks.id'))
    participations = db.relationship("Participation", backref="tournament", lazy="dynamic")
    players = db.relationship("TournamentPlayer", backref="tournament", lazy="dynamic")
    matches = db.relationship("Match", backref="tournament", lazy="dynamic")

    def __repr__(self):
        return self.name

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

    def is_open_to_registration(self):
        return self.status == TournamentStatus.REGISTRATION_OPEN

    def is_ongoing(self):
        return self.status == TournamentStatus.ONGOING

    def is_finished(self):
        return self.status == TournamentStatus.FINISHED

    def get_matches_first_round(self):
        return [m for m in self.matches if m.round == self.number_rounds]

    def is_draw_created(self):
        players = (TournamentPlayer.query
                   .filter(TournamentPlayer.tournament_id == self.id))
        return players.first() is not None

    def get_matches_by_round(self):
        return [{"round": i,
                 "matches": self.matches.filter(Match.round == i).all(),
                 "first_round": i == self.number_rounds}
                for i in range(self.number_rounds, 0, -1)]

    def get_last_match(self):
        return self.matches.filter(Match.position == 1).first()

    def get_round_names(self):
        names = ["F", "DF", "QF", "HF"]
        if self.number_rounds > 4:
            names += ["T" + str(i)
                      for i in range(self.number_rounds - 4, 0, -1)]
            return names[::-1]
        else:
            return names[:self.number_rounds][::-1]

    def get_attributed_points(self):
        return tournament_categories.get(self.category)["points"]

    def get_allowed_forecasts(self):
        players = [p for p in self.players
                   if not p.is_bye() and p.player_id]
        return players

    def compute_scores(self):
        for p in self.participations:
            p.points = p.compute_score()
            p.round_reached = p.tournament_player.get_last_match().round - 1
            db.session.add(p)
        db.session.commit()

    @staticmethod
    def get_latest_finished_tournament():
        return (
            Tournament.query
                .order_by(Tournament.started_at.desc())
                .filter(Tournament.status == TournamentStatus.FINISHED)
                .first()
        )


class Participation(db.Model):
    __tablename__ = "participations"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    deleted_at = db.Column(db.DateTime, default=None)
    round_reached = db.Column(db.Integer)
    points = db.Column(db.Integer)

    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    tournament_player_id = db.Column(db.Integer, db.ForeignKey('tournament_players.id'))

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def has_made_forecast(self):
        return self.tournament_player_id is not None

    def get_forbidden_forecasts(self):
        if self.tournament.category == "World Tour Finals":
            return []
        players = self.tournament.get_allowed_forecasts()
        current_year = func.year(self.tournament.week.start_date)
        current_year_participations = (
            self.user.participations
                .join(Tournament)
                .join(TournamentWeek)
                .filter(func.year(TournamentWeek.start_date) == current_year)
                .filter(Participation.id != self.id)
        )
        players_already_picked = [
            p.tournament_player.player_id
            for p in current_year_participations
            if p.tournament_player
        ]
        return [p.id for p in players
                if p.player_id in players_already_picked]

    def compute_score(self):
        if self.tournament.category == "World Tour Finals":
            return self.points or 0
        points = self.tournament.get_attributed_points()
        if self.tournament_player.has_won_tournament():
            return points[0]
        elif self.tournament_player.has_lost_after_bye():
            return points[-1]
        else:
            last_match = self.tournament_player.get_last_match()
            return points[last_match.round]

    def get_status(self):
        return self.tournament_player.get_status()

    def get_ranking(self):
        week_id = self.tournament.week_id
        ranking = (
            Ranking.query
                .filter(Ranking.tournament_week_id == week_id)
                .filter(Ranking.user_id == self.user_id)
                .first()
        )
        if ranking:
            return ranking.year_to_date_ranking
        return None


class Player(db.Model):
    __tablename__ = "players"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    deleted_at = db.Column(db.DateTime, default=None)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    tournament_players = db.relationship("TournamentPlayer", backref="player", lazy="dynamic")

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def get_name(self, format="standard"):
        if format == "standard":
            return f"{self.first_name} {self.last_name.upper()}"
        elif format == "last_name_first":
            return f"{self.last_name.upper()}, {self.first_name}"
        elif format == "first_name_initial":
            if self.first_name:
                return f"{self.first_name[0]}. {self.last_name.upper()}"
            else:
                return self.last_name.upper()

    @classmethod
    def get_all(cls, format="last_name_first"):
        return [(p.id, p.get_name(format))
                for p in cls.query.order_by(cls.last_name, cls.first_name).all()]


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
    participations = db.relationship("Participation", backref="tournament_player", lazy="dynamic")

    def __repr__(self):
        return f"{self.id}, {self.get_name()}"

    def get_name(self, format="full"):
        if self.player is None:
            full_name = ""
            if self.status:
                full_name += f"[{self.status}] "
            if self.seed:
                full_name += f"[{self.seed}] "
            full_name += f"Qualifié {self.qualifier_id}"
            return full_name
        if format == "full":
            full_name = ""
            if self.status:
                full_name += f"[{self.status}] "
            if self.seed:
                full_name += f"[{self.seed}] "
            full_name += self.player.get_name(format="first_name_initial")
            return full_name
        else:
            return self.player.get_name(format)

    def get_opponent(self, match):
        if self.id == match.tournament_player1_id:
            return match.tournament_player2

        elif self.id == match.tournament_player2_id:
            return match.tournament_player1

        else:
            raise ValueError("This player did not play this match")

    def is_bye(self):
        return (
                self.player and
                self.player.last_name == "Bye" and
                self.player.first_name == ""
        )

    def get_last_match(self):
        return self.matches.order_by(Match.round).first()

    def has_lost(self):
        last_match = self.get_last_match()
        return (last_match.winner is not None and
                last_match.winner_id != self.id)

    def has_won_tournament(self):
        final_match = (
            self.matches
                .filter(Match.round == 1)
                .filter(Match.winner_id == self.id)
                .first()
        )
        return final_match is not None

    @property
    def ordered_matches(self):
        return self.matches.order_by(Match.round.desc())

    @property
    def first_match(self):
        return self.ordered_matches.first()

    def has_lost_after_bye(self):
        if not self.get_opponent(self.first_match).is_bye():
            return False

        if self.ordered_matches.count() <= 1:
            return False

        next_match = self.ordered_matches.all()[1]
        return next_match.winner is None or next_match.winner_id != self.id

    def get_status(self):
        last_match = self.get_last_match()
        round_names = self.tournament.get_round_names()
        round_name = round_names[::-1][last_match.round - 1]

        if self.has_lost():
            return f"Eliminé ({round_name}) <span class='fa fa-times'></span>"

        if self.has_won_tournament():
            return "Vainqueur <span class='fa fa-trophy'></span>"

        return f"En course ({round_name})"


class Match(db.Model):
    __tablename__ = "matches"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    deleted_at = db.Column(db.DateTime)

    position = db.Column(db.Integer)
    round = db.Column(db.Integer)

    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.id'))
    winner_id = db.Column(db.Integer, db.ForeignKey('tournament_players.id'))
    winner = db.relationship("TournamentPlayer", foreign_keys="Match.winner_id")
    tournament_player1_id = db.Column(db.Integer, db.ForeignKey('tournament_players.id'))
    tournament_player2_id = db.Column(db.Integer, db.ForeignKey('tournament_players.id'))
    tournament_player1 = db.relationship("TournamentPlayer", foreign_keys="Match.tournament_player1_id")
    tournament_player2 = db.relationship("TournamentPlayer", foreign_keys="Match.tournament_player2_id")

    def get_previous_match(self, position):
        if self.round == self.tournament.number_rounds:
            return None

        return (
            Match.query
                .filter(Match.tournament_id == self.tournament_id)
                .filter(Match.position == 2 * self.position + position)
                .first()
        )

    def get_next_match(self):
        if self.round == 1:
            return None

        return (
            Match.query
                .filter(Match.tournament_id == self.tournament_id)
                .filter(Match.position == self.position // 2)
                .first()
        )

    def has_bye(self):
        if self.round < self.tournament.number_rounds:
            return False

        return (
                (self.tournament_player1 and self.tournament_player1.is_bye()) or
                (self.tournament_player2 and self.tournament_player2.is_bye())
        )


class Ranking(db.Model):
    __tablename__ = "rankings"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    deleted_at = db.Column(db.DateTime)

    year_to_date_points = db.Column(db.Integer)
    year_to_date_ranking = db.Column(db.Integer)
    year_to_date_number_tournaments = db.Column(db.Integer)

    tournament_week_id = db.Column(db.Integer, db.ForeignKey('tournament_weeks.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return (f"User {self.user_id}, {self.year_to_date_points} points " +
                f"(#{self.year_to_date_ranking})")

    @staticmethod
    def compute_rankings(week=None):
        if week is None:
            week = Tournament.get_latest_finished_tournament().week

        year = week.start_date.year

        participations = (
            Participation.query
                .join(Tournament)
                .join(TournamentWeek)
                .filter(TournamentWeek.start_date <= week.start_date)
                .filter(TournamentWeek.start_date >= datetime.date(year - 1, 12, 25))
                .filter(Tournament.status == TournamentStatus.FINISHED)
        )

        scoreboard = {}
        for p in participations:
            if p.user_id in scoreboard:
                scoreboard[p.user_id]["points"] += p.points
                scoreboard[p.user_id]["number_tournaments"] += 1
            else:
                scoreboard[p.user_id] = {
                    "points": p.points,
                    "number_tournaments": 1
                }

        scoreboard = [{
            "user_id": k,
            "points": v["points"],
            "number_tournaments": v["number_tournaments"],
        } for k, v in scoreboard.items()]

        scoreboard = sorted(scoreboard, key=lambda x: -x["points"])

        for rank, score in enumerate(scoreboard):
            r = (
                Ranking.query
                    .filter(Ranking.tournament_week_id == week.id)
                    .filter(Ranking.user_id == score["user_id"]).first()
            )
            if r is None:
                r = Ranking(
                    user_id=score["user_id"],
                    tournament_week_id=week.id
                )

            r.year_to_date_points = score["points"]
            r.year_to_date_ranking = rank + 1
            r.year_to_date_number_tournaments = score["number_tournaments"]
            db.session.add(r)

        db.session.commit()
