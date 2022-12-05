from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils.html import strip_tags


@shared_task(bind = True)
def send_email_through_celery(self, subject, html_content, recepient):
    text_content = strip_tags(html_content)
    email = EmailMultiAlternatives(
            subject,
            text_content,
            settings.EMAIL_HOST,
            [recepient]
            )
    email.attach_alternative(html_content, "text/html")
    email.send()
    return subject + ' EMAIL SENT'