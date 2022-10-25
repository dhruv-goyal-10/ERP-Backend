from django.core.mail import EmailMessage
import random
from django.conf import settings
from . models import User

# def send_otp_via_email(email):
#     subject = "EDUMATE PASSWORD RESET"
#     otp = random.randint(1000,9999)
#     msg = f'YOUR EDUMATE PASSWORD RESET OTP IS {otp}'
#     email_from = settings.EMAIL_HOST
#     send_mail(subject, msg, email_from, [email])
#     user_obj = User.objects.get(email=email)
#     user_obj.otp = otp
#     user_obj.save()


class EMAIL:
    @staticmethod
    def send_otp_via_email(mailaddress):
        otp = random.randint(1000,9999)
        email = EmailMessage(
            subject = "EDUMATE PASSWORD RESET",
            body = f'YOUR EDUMATE PASSWORD RESET OTP IS {otp}',
            from_email = settings.EMAIL_HOST,
            to=[mailaddress]
        )
        email.send()
        