from django.core.mail import EmailMessage
import random
from django.conf import settings
from . models import User

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
        # email.send()
        user = User.objects.get(email=mailaddress)
        user.otp = otp
        user.save()