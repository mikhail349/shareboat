import os

EMAIL_HOST = os.environ['EMAIL_HOST']
EMAIL_PORT = os.environ['EMAIL_PORT']
EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']
EMAIL_USE_SSL = os.environ['EMAIL_USE_SSL']
DEFAULT_FROM_EMAIL = os.environ['DEFAULT_FROM_EMAIL']
SERVER_EMAIL = os.environ['SERVER_EMAIL']
EMAIL_LAG_MINUTES = int(os.environ.get('EMAIL_LAG_MINUTES', 1))
