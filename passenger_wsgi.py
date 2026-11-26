import sys
import os

app_dir = os.path.dirname(__file__)
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

from app import app as application
