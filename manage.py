from flask_script import Manager, Shell, Command, Option
from app import create_app

def make_shell_context():
    return dict(app = app)

app = create_app("dev")
manager = Manager(app)
manager.add_command("shell", Shell(make_context = make_shell_context))

if __name__ == "__main__":
    manager.run()
