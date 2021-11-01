from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from shareboat.tokens import account_activation_token
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from shareboat.email import send_email

def send_verification_email(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_activation_token.make_token(user)
    domain = ("https" if request.is_secure() else "http") + "://" + get_current_site(request).domain
    html = render_to_string("user/verification_email.html", context={'uid': uid, 'token': token, 'domain': domain})
    send_email("Подтверждение почты", html, [user.email])