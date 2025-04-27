"""
ASGI config for agrifinance project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agrifinance.settings')

application = get_asgi_application()
