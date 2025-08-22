# Standard library imports
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

# Django imports
from django.core.wsgi import get_wsgi_application  # noqa: E402

application = get_wsgi_application()
