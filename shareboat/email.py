from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_email(subject, content, recipients):
    html = render_to_string("email.html", context={'content': content})
    plain_message = strip_tags(html)
    return send_mail("ShareBoat - %s" % subject, plain_message, None, recipients, html_message=html)