from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell

from app import create_app, db
from app.models import Match, Participation, Player, Ranking, Role, Tournament, TournamentPlayer, TournamentStatus, \
    TournamentWeek, User
from instance import instance


def make_shell_context():
    return dict(app=app,
                db=db,
                Match=Match,
                Participation=Participation,
                Player=Player,
                Ranking=Ranking,
                Role=Role,
                Tournament=Tournament,
                TournamentPlayer=TournamentPlayer,
                TournamentStatus=TournamentStatus,
                TournamentWeek=TournamentWeek,
                User=User,
                )


app = create_app(instance)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command("db", MigrateCommand)
manager.add_command("shell", Shell(make_context=make_shell_context))


if __name__ == "__main__":
    manager.run()
