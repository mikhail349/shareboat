from django.contrib.auth.tokens import PasswordResetTokenGenerator
from shareboat.settings import SECRET_KEY

# Не используется
class TokenGenerator(PasswordResetTokenGenerator):
    key_salt = SECRET_KEY

    def _make_hash_value(self, user, timestamp):
        return str(user.pk) + str(timestamp) + str(user.is_active) + str(self.key_salt)

      
verification_email_token = TokenGenerator()