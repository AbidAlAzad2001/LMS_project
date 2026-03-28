"""
WSGI config for Django LMS on PythonAnywhere.

This file is used by PythonAnywhere to serve the Django application.
Place this file in your project root.
"""

import os
import sys

# Add your project directory to the path
project_home = os.path.expanduser('~/lms_ai')
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Switch to the project directory
os.chdir(project_home)

# Set the settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'lms_ai.settings'

# Import Django's WSGI handler
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
