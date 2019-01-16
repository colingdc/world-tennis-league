import csv
import random
from datetime import datetime, timedelta

from faker import Faker
from flask_script import Command, Option

from app import db
from app.models import (Participation, Player, Ranking, Role, Tournament,
                        TournamentStatus, TournamentWeek, User)


class CreateFakeUsers(Command):
    option_list = (
        Option('--number_users', '-n', dest='number_users'),
    )

    def run(self, number_users):
        if number_users is None:
            number_users = 10
        else:
            number_users = int(number_users)

        Role.insert_roles()
        user_role = Role.query.filter(Role.name == "User").first()

        f = Faker()

        for i in range(number_users):
            u = User(
                email=f.email(),
                username=f.name(),
                password=f.password(),
                confirmed=True,
                role_id=user_role.id,
            )
            db.session.add(u)
            print(f"User #{i + 1} {u.username} created")
        db.session.commit()


class CreateUsers(Command):
    def run(self):
        role = Role.query.filter_by(name="User").first()
        with open("data/users.csv") as f:
            for row in f.readlines():
                username = row.strip()
                u = User(username=username,
                         email=f"{username}@test.com",
                         password="password",
                         role=role,
                         confirmed=True)
                db.session.add(u)
                print(f"Added user {username}")
            db.session.commit()


class CreateSpecialUsers(Command):
    def run(self):
        Role.insert_roles()
        manager_role = Role.query.filter(
            Role.name == "Tournament Manager").first()
        admin_role = Role.query.filter(Role.name == "Administrator").first()

        manager = User(
            email="manager@gmail.com",
            username="manager",
            password="manager123",
            confirmed=True,
            role_id=manager_role.id,
        )
        admin = User(
            email="admin@gmail.com",
            username="admin",
            password="admin123",
            confirmed=True,
            role_id=admin_role.id,
        )
        db.session.add(manager)
        db.session.add(admin)
        db.session.commit()
        print("Admin and tournament manager users created")


class CreateFakeTournaments(Command):
    option_list = (
        Option('--number_weeks', '-n', dest='number_weeks'),
    )

    def run(self, number_weeks):
        if number_weeks is None:
            number_weeks = 10
        else:
            number_weeks = int(number_weeks)

        f = Faker()

        for i in range(number_weeks):
            d = datetime.strptime(f.date(), "%Y-%m-%d")
            start_date = d - timedelta(days=d.weekday())
            w = TournamentWeek(
                start_date=start_date
            )
            db.session.add(w)
            db.session.commit()
            print(f"Week #{i + 1} created")

            number_tournaments = random.randint(1, 3)
            for j in range(number_tournaments):
                t = Tournament(
                    name=f"{f.city()} {start_date.year}",
                    started_at=d,
                    week_id=w.id,
                )
                db.session.add(t)
                print(f"-- Tournament #{j + 1} {t.name} created")
            db.session.commit()


class CreateFakePlayers(Command):
    option_list = (
        Option('--number_players', '-n', dest='number_players'),
    )

    def run(self, number_players):
        if number_players is None:
            number_players = 10
        else:
            number_players = int(number_players)

        f = Faker()

        for i in range(number_players):
            p = Player(
                first_name=f.first_name(),
                last_name=f.last_name(),
            )
            db.session.add(p)
            print(f"Player #{i + 1} {p.get_name()} created")
        db.session.commit()


class CreateATPPlayers(Command):
    def run(self):
        with open("data/atp_players.csv") as f:
            for row in f.readlines():
                first_name, last_name = row.strip().split(",")
                p = Player(
                    first_name=first_name,
                    last_name=last_name,
                )
                db.session.add(p)
                print(f"Player {p.get_name()} created")
            db.session.commit()


class CreateByePlayer(Command):
    def run(self):
        p = Player(
            first_name="",
            last_name="Bye",
        )
        db.session.add(p)
        db.session.commit()
        print(f"Player BYE created")


class CreateTemporaryAccounts(Command):
    def run(self):
        f = Faker()
        role = Role.query.filter_by(name="User").first()
        with open("data/WTL.csv") as csv_file:
            reader = csv.DictReader(csv_file, delimiter=";")
            for row in reader:
                email = "TEMPORARY_" + row["\ufeffMail"]
                username = row["Pseudo"] + " [compte temporaire]"
                u = User(username=username,
                         email=email,
                         password=f.password(),
                         role=role,
                         confirmed=True)
                db.session.add(u)
                db.session.commit()
                print(f"Added user {username}")

                for (t_id, p_id) in (("T1", "P1"), ("T2", "P2"), ("T3", "P3")):
                    if row[t_id]:
                        p = Participation(
                            user_id=u.id,
                            tournament_id=int(row[t_id]),
                            tournament_player_id=int(row[p_id]),
                        )
                        db.session.add(p)
                        print(f"---Tournament {t_id} added")


class CloseTournament(Command):
    option_list = (
        Option('--tournament_id', '-i', dest='tournament_id'),
    )

    def run(self, tournament_id):
        tournament = Tournament.query.get(tournament_id)
        tournament.status = TournamentStatus.FINISHED
        db.session.add(tournament)
        db.session.commit()
        tournament.compute_scores()
        Ranking.compute_rankings(tournament.week)
