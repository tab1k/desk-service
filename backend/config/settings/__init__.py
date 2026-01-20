"""
Django settings module initialization.
Automatically loads the appropriate settings based on DJANGO_SETTINGS_MODULE environment variable.
"""
import os

# Determine which settings to use based on environment
ENVIRONMENT = os.getenv('DJANGO_ENVIRONMENT', 'development')

if ENVIRONMENT == 'production':
    from .production import *
elif ENVIRONMENT == 'development':
    from .development import *
else:
    from .development import *
