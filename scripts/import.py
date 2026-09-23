"""
python import.py export.zip
"""

import os
import sys

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from CTFd import create_app
from CTFd.utils.exports import import_ctf

import sys

app = create_app()
with app.app_context():
    print(
        "This file will be deleted in CTFd v4.0. Switch to using `python manage.py import_ctf`"
    )
    import_ctf(sys.argv[1])
