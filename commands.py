import random
from datetime import datetime, timedelta

from faker import Faker
from flask_script import Command, Option

from app import db
from app.models import Role, Tournament, TournamentWeek, User, Player


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
                    name=" ".join(f.words(3)),
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
