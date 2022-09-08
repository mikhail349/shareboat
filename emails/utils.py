from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils.html import strip_tags


import logging
logger = logging.getLogger(__name__)


def send_email(subject, content, recipients):
    html = render_to_string("emails/email.html", context={'content': content})
    plain_message = strip_tags(html)
    try:
        res = send_mail("SHAREBOAT.RU - %s" % subject,
                        plain_message, None, recipients, html_message=html)
    except Exception as e:
        logger.error(str(e))
        raise e
    return res
