from django.conf import settings
import datetime
import jwt
from .exceptions import InvalidToken

VERIFICATION = 'verification'
RESTORE_PASSWORD = 'restore_password'

def generate_token(user, type, minutes=15, seconds=0):
    
    token_payload = {
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, minutes=minutes, seconds=seconds),
        'iat': datetime.datetime.utcnow(),    
        'type': type
    }

    return jwt.encode(token_payload, settings.SECRET_KEY, algorithm='HS256').decode('utf-8')

def check_token(token, type):
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    if payload.get('type') != type:
        raise InvalidToken("Неверный токен")
    return payload