from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.utils.html import strip_tags

from shareboat.tokens import account_activation_token
#from emails.models import UserEmail

import logging
logger = logging.getLogger(__name__)

def send_email(subject, content, recipients):
    html = render_to_string("emails/email.html", context={'content': content})
    plain_message = strip_tags(html)
    try:
        res = send_mail("ShareBoat - %s" % subject, plain_message, None, recipients, html_message=html) 
    except Exception as e:
        logger.error(str(e))
        raise e
    return res

'''
def send_verification_email(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_activation_token.make_token(user)
    domain = ("https" if request.is_secure() else "http") + "://" + get_current_site(request).domain
    html = render_to_string("emails/verification_email.html", context={'uid': uid, 'token': token, 'domain': domain})
    send_email("Подтверждение почты", html, [user.email])
    UserEmail.objects.update_or_create(user=user, type=UserEmail.Type.VERIFICATION)
'''

