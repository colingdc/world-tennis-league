import datetime

from flask import current_app
from flask_babel import _
from flask_login import AnonymousUserMixin, UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from sqlalchemy import func

from . import bcrypt, db, login_manager
from .constants import Permission, roles, tournament_categories


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    confirmed = db.Column(db.Boolean, default=False)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True)
    password_hash = db.Column(db.String(128))
    notifications_activated = db.Column(db.Boolean, default=False)
    role_id = db.Column(db.Integer)
    participations = db.relationship("Participation", backref="user", lazy="dynamic")
    rankings = db.relationship("Ranking", backref="user", lazy="dynamic")

    def is_anonymous(self):
        return False

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

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

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def can(self, permissions):
        if self.role_id is None:
            return False

        return (roles[self.role_id]["permissions"] & permissions) == permissions

    def get_role_name(self):
        return roles[self.role_id]["name"]

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
        return self.get_participation(tournament) is not None

    def can_make_forecast(self, tournament):
        return (
                tournament.status == TournamentStatus.REGISTRATION_OPEN
                and self.is_registered_to_tournament(tournament)
        )

    def get_participation(self, tournament):
        return (
            self.participations
                .join(Tournament)
                .filter(Tournament.id == tournament.id).first()
        )

    def make_forecast(self, tournament, tournament_player_id):
        participation = self.get_participation(tournament)
        participation.tournament_player_id = tournament_player_id
        db.session.add(self)
        db.session.commit()

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

    def is_manager(self):
        return False

    def is_anonymous(self):
        return True


login_manager.anonymous_user = AnonymousUser


class TournamentWeek(db.Model):
    __tablename__ = "tournament_weeks"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    start_date = db.Column(db.Date)
    tournaments = db.relationship("Tournament", backref="week", lazy="dynamic")
    rankings = db.relationship("Ranking", backref="week", lazy="dynamic")

    def get_short_name(self):
        year, week_number, _ = self.start_date.isocalendar()
        return f"{year} Semaine {week_number}"

    def get_long_name(self):
        year, week_number, _ = self.start_date.isocalendar()
        tournament_names = ", ".join([t.name for t in self.tournaments])
        return f"{week_number} {year} - {tournament_names}"

    def get_full_name(self):
        return "Semaine " + self.get_long_name()


class TournamentStatus:
    CREATED = 10
    REGISTRATION_OPEN = 20
    ONGOING = 30
    FINISHED = 40


class Tournament(db.Model):
    __tablename__ = "tournaments"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)

    name = db.Column(db.String(64))
    started_at = db.Column(db.DateTime)
    number_rounds = db.Column(db.Integer)
    category = db.Column(db.String(64))
    status = db.Column(db.Integer, default=TournamentStatus.CREATED)
    notification_sent_at = db.Column(db.DateTime)

    week_id = db.Column(db.Integer, db.ForeignKey("tournament_weeks.id"))
    participations = db.relationship("Participation", backref="tournament", lazy="dynamic")
    players = db.relationship("TournamentPlayer", backref="tournament", lazy="dynamic")
    matches = db.relationship("Match", backref="tournament", lazy="dynamic")

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def get_status(self):
        if self.status == TournamentStatus.CREATED:
            return _("tournament_status_created")
        if self.status == TournamentStatus.REGISTRATION_OPEN:
            return _("tournament_status_registration_open")
        if self.status == TournamentStatus.ONGOING:
            return _("tournament_status_ongoing")
        if self.status == TournamentStatus.FINISHED:
            return _("tournament_status_finished")

    def is_special_tournament(self):
        return self.category == "World Tour Finals"

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
        if self.tournament.is_special_tournament():
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
        if self.tournament.is_special_tournament():
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
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    tournament_players = db.relationship("TournamentPlayer", backref="player", lazy="dynamic")

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def get_standard_name(self):
        return f"{self.first_name} {self.last_name.upper()}"

    def get_reversed_name(self):
        return f"{self.last_name.upper()}, {self.first_name}"

    def get_short_name(self):
        if self.first_name:
            return f"{self.first_name[0]}. {self.last_name.upper()}"
        else:
            return self.last_name.upper()

    @classmethod
    def get_all(cls):
        return [
            (p.id, p.get_reversed_name())
            for p in cls.query.order_by(cls.last_name, cls.first_name).all()
        ]


class TournamentPlayer(db.Model):
    __tablename__ = "tournament_players"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
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

    def get_qualifier_name(self):
        return f"Qualifié {self.qualifier_id}"

    def get_full_name(self):
        full_name = ""
        if self.status:
            full_name += f"[{self.status}] "
        if self.seed:
            full_name += f"[{self.seed}] "
        if self.player is None:
            return full_name + self.get_qualifier_name()
        else:
            return full_name + self.player.get_short_name()

    def get_standard_name(self):
        if self.player is None:
            return self.get_qualifier_name()
        else:
            return self.player.get_standard_name()

    def get_reversed_name(self):
        if self.player is None:
            return self.get_qualifier_name()
        else:
            return self.player.get_reversed_name()

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
            return {"status": "lost", "round_name": round_name}
        elif self.has_won_tournament():
            return {"status": "won_tournament"}
        else:
            return {"status": "still_playing", "round_name": round_name}


class Match(db.Model):
    __tablename__ = "matches"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)

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

    year_to_date_points = db.Column(db.Integer)
    year_to_date_ranking = db.Column(db.Integer)
    year_to_date_number_tournaments = db.Column(db.Integer)

    tournament_week_id = db.Column(db.Integer, db.ForeignKey('tournament_weeks.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

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
        for participation in participations:
            if participation.user_id in scoreboard:
                scoreboard[participation.user_id]["points"] += participation.points
                scoreboard[participation.user_id]["number_tournaments"] += 1
            else:
                scoreboard[participation.user_id] = {
                    "points": participation.points,
                    "number_tournaments": 1
                }

        scoreboard = [{
            "user_id": user_id,
            "points": stats["points"],
            "number_tournaments": stats["number_tournaments"],
        } for user_id, stats in scoreboard.items()]

        scoreboard = sorted(scoreboard, key=lambda stats: -stats["points"])

        for rank, score in enumerate(scoreboard):
            ranking = (
                Ranking.query
                    .filter(Ranking.tournament_week_id == week.id)
                    .filter(Ranking.user_id == score["user_id"]).first()
            )
            if ranking is None:
                ranking = Ranking(
                    user_id=score["user_id"],
                    tournament_week_id=week.id
                )

            ranking.year_to_date_points = score["points"]
            ranking.year_to_date_ranking = rank + 1
            ranking.year_to_date_number_tournaments = score["number_tournaments"]
            db.session.add(ranking)

        db.session.commit()
