import os
import sys

# Ensure root project directory is in sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Set VERCEL environment variable to trigger serverless adaptations
os.environ["VERCEL"] = "1"

# Import CTFd application factory
from CTFd import create_app

# Create WSGI application object for Vercel Python runtime
app = create_app()
