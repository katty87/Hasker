from Hasker.settings.base import *


DEBUG = True

SECRET_KEY = '!q^vwef^38%+1a_f@icc73q6by#==)=zca)sgp)tlq&1owzox)'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'haskerdb',
        'USER': 'django',
        'PASSWORD': 'django',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}