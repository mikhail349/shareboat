from pathlib import Path
import os
import sys

import dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

dotenv_file = os.path.join(BASE_DIR, ".env")
if os.path.isfile(dotenv_file):
    dotenv.load_dotenv(dotenv_file)

SECRET_KEY = os.environ['SECRET_KEY']
DEBUG = ('runserver' in sys.argv) or ('test' in sys.argv)

ALLOWED_HOSTS = ['*']
AUTH_USER_MODEL = 'user.User'

INSTALLED_APPS = [
    'rest_framework',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    'django_summernote',
    'coverage',

    'user',
    'file',
    'boat',
    'emails',
    'booking',
    'notification',
    'base',
    'telegram_bot',
    'chat',
    'portal'
]

SUMMERNOTE_THEME = 'bs4'
SUMMERNOTE_CONFIG = {
    'summernote': {
        'width': '100%'
    }
}

REST_FRAMEWORK = {

    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    )
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'shareboat.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, "templates"),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'shareboat.context_processors.nav_counters',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],

            'libraries': {
                'extras': 'shareboat.templatetags.extras'
            }
        },
    },
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'environment': 'shareboat.jinja2.environment'
        },
    },
]

WSGI_APPLICATION = 'shareboat.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ['DATABASE_NAME'],
        'USER': os.environ['DATABASE_USER'],
        'PASSWORD': os.environ['DATABASE_PASSWORD'],
        'HOST': os.environ['DATABASE_HOST'],
        'PORT': int(os.environ['DATABASE_PORT'])
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = os.environ['TIME_ZONE']
USE_I18N = True
USE_L10N = True
USE_TZ = True

USE_THOUSAND_SEPARATOR = True
PREPAYMENT_DAYS_LIMIT = os.environ.get('PREPAYMENT_DAYS_LIMIT', 5)
ADMIN_URL = os.environ.get('ADMIN_URL', 'admin')

PAGINATOR_BOAT_PER_PAGE = os.environ.get('PAGINATOR_BOAT_PER_PAGE', 15)
PAGINATOR_ARTICLE_PER_PAGE = os.environ.get('PAGINATOR_ARTICLE_PER_PAGE', 15)

MEDIA_ROOT = os.environ['MEDIA_ROOT']
MEDIA_URL = '/uploads/'

STATIC_ROOT = os.environ['STATIC_ROOT']
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
LOGIN_URL = '/user/login/'

EMAIL_HOST = os.environ['EMAIL_HOST']
EMAIL_PORT = os.environ['EMAIL_PORT']
EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']
EMAIL_USE_SSL = os.environ['EMAIL_USE_SSL']
DEFAULT_FROM_EMAIL = os.environ['DEFAULT_FROM_EMAIL']
SERVER_EMAIL = os.environ['SERVER_EMAIL']

RECAPTCHA_CLIENTSIDE_KEY = os.environ.get('RECAPTCHA_CLIENTSIDE_KEY')
RECAPTCHA_SERVERSIDE_KEY = os.environ.get('RECAPTCHA_SERVERSIDE_KEY')

TGBOT_TOKEN = os.environ['TGBOT_TOKEN']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
ADMINS = list(eval((os.environ['ADMINS'])))

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(os.environ['LOGGER_ROOT'], 'shareboat.log'),
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'tgbot_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(os.environ['LOGGER_ROOT'], 'tgbot_shareboat.log'),
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'mail_admins': {
            'class': 'django.utils.log.AdminEmailHandler',
        },
        'mail_admins_error': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'root': {
        'handlers': ['file', 'console'],
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console', 'mail_admins_error'],
            'level': 'INFO',
            'propagate': False,
        },
        'tgbot': {
            'handlers': ['tgbot_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'mail_admins': {
            'handlers': ['file', 'console', 'mail_admins'],
            'propagate': False,
        },
    }
}
