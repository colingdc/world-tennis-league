from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell

from app import create_app, db


def make_shell_context():
    return dict(app=app)


app = create_app("dev")
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command("db", MigrateCommand)
manager.add_command("shell", Shell(make_context=make_shell_context))

if __name__ == "__main__":
    manager.run()
