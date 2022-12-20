from pathlib import Path
import os
import sys

import dotenv
from split_settings.tools import include


BASE_DIR = Path(__file__).resolve().parent.parent

dotenv_file = os.path.join(BASE_DIR, ".env")
if os.path.isfile(dotenv_file):
    dotenv.load_dotenv(dotenv_file)

include(
    'components/apps.py',
    'components/summernote.py',
    'components/drf.py',
    'components/middleware.py',
    'components/templates.py',
    'components/databases.py',
    'components/logging.py',
    'components/email.py'
)

SECRET_KEY = os.environ['SECRET_KEY']
DEBUG = ('runserver' in sys.argv) or ('test' in sys.argv)
ALLOWED_HOSTS = ['*']
AUTH_USER_MODEL = 'user.User'
ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'NumericPasswordValidator',
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
MEDIA_URL = '/media/'

STATIC_ROOT = os.environ['STATIC_ROOT']
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]

STATICFILES_STORAGE = ('django.contrib.staticfiles.storage.'
                       'ManifestStaticFilesStorage')


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
ADMINS = list(eval((os.environ['ADMINS'])))
LOGIN_URL = '/user/login/'

RECAPTCHA_CLIENTSIDE_KEY = os.environ.get('RECAPTCHA_CLIENTSIDE_KEY')
RECAPTCHA_SERVERSIDE_KEY = os.environ.get('RECAPTCHA_SERVERSIDE_KEY')

TGBOT_TOKEN = os.environ['TGBOT_TOKEN']
