import logging

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


def send_email(subject: str, content: str, recipients: list[str]) -> int:
    """Отправить письмо.

    Args:
        subject: тема
        content: содержимое в формате HTML
        recipients: список email получателей

    Returns:
        int: код отправки

    """
    html = render_to_string("emails/email.html", context={'content': content})
    plain_message = strip_tags(html)
    try:
        res = send_mail("SHAREBOAT.RU - %s" % subject,
                        plain_message, None, recipients, html_message=html)
    except Exception as e:
        logger.error(str(e))
        raise e
    return res
