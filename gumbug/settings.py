import sys
import os
import dj_database_url

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = '&#zrr92u6yn!l9^ycc)f-0kh(tigr94z=mx6phl0cyhk)9eps!'

ON_PRODUCTION_SERVER = 'ON_PRODUCTION_SERVER' in os.environ
DEBUG = not ON_PRODUCTION_SERVER  # False for live site
TEMPLATE_DEBUG = DEBUG


ALLOWED_HOSTS = [
    ".floating-forest-4090.herokuapp.com"
]


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'gumbug',
)

if ON_PRODUCTION_SERVER:
    INSTALLED_APPS += ('gunicorn',)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'gumbug.urls'

WSGI_APPLICATION = 'gumbug.wsgi.application'


# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

if ON_PRODUCTION_SERVER:
    DATABASES = {
        'default': dj_database_url.config()
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = 'staticfiles'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '[%(asctime)s] %(levelname)s %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'stream': sys.stdout,
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['default'],
            'level': 'ERROR',
            'propagate': True,
        },
        '': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': True
        },
    }
}
