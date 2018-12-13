from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell

from app import create_app, db
from commands import CreateFakeUsers, CreateSpecialUsers, CreateFakeTournaments
from app.models import (User, Role, Tournament,
                        TournamentWeek, TournamentStatus)


def make_shell_context():
    return dict(app=app,
                db=db,
                User=User,
                Role=Role,
                Tournament=Tournament,
                TournamentWeek=TournamentWeek,
                TournamentStatus=TournamentStatus,
                )


app = create_app("dev")
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command("db", MigrateCommand)
manager.add_command("shell", Shell(make_context=make_shell_context))


manager.add_command("create_fake_users", CreateFakeUsers())
manager.add_command("create_special_users", CreateSpecialUsers())
manager.add_command("create_fake_tournaments", CreateFakeTournaments())


if __name__ == "__main__":
    manager.run()
