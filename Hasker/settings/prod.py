from Hasker.settings.base import *
import os
from django.core.exceptions import ImproperlyConfigured


def get_env_value(env_variable):
    try:
        return os.environ[env_variable]
    except KeyError:
        error_msg = 'Set the {} environment variable'.format(env_variable)
        raise ImproperlyConfigured(error_msg)


SECRET_KEY = get_env_value("SECRET_KEY")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'haskerdb',
        'USER': 'django',
        'PASSWORD': 'django',
        'HOST': 'db',
        'PORT': '5432',
    }
}
