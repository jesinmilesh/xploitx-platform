import os
import sys

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from flask.cli import FlaskGroup

from CTFd import create_app

app = create_app()

cli = FlaskGroup(app)


if __name__ == "__main__":
    cli()
