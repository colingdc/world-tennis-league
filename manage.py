from commands import (CloseTournament, CreateATPPlayers, CreateByePlayer,
                      CreateFakePlayers, CreateFakeTournaments,
                      CreateFakeUsers, CreateSpecialUsers,
                      CreateTemporaryAccounts, CreateUsers, MergeAccounts,
                      MergeAllAccounts, SendNewTournamentsEmail)

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell

from app import create_app, db
from app.models import (Match, Participation, Player, Ranking, Role,
                        Tournament, TournamentPlayer, TournamentStatus,
                        TournamentWeek, User)
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


manager.add_command("create_fake_users", CreateFakeUsers())
manager.add_command("create_special_users", CreateSpecialUsers())
manager.add_command("create_users", CreateUsers())
manager.add_command("create_fake_tournaments", CreateFakeTournaments())
manager.add_command("create_fake_players", CreateFakePlayers())
manager.add_command("create_atp_players", CreateATPPlayers())
manager.add_command("create_bye_player", CreateByePlayer())
manager.add_command("create_temporary_accounts", CreateTemporaryAccounts())
manager.add_command("close_tournament", CloseTournament())
manager.add_command("merge_accounts", MergeAccounts())
manager.add_command("merge_all_accounts", MergeAllAccounts())
manager.add_command("send_new_tournaments_email", SendNewTournamentsEmail())


if __name__ == "__main__":
    manager.run()
