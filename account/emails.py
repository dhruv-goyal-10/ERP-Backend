from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import random
from django.utils import timezone
from django.conf import settings
from . models import *


class EMAIL:
    @staticmethod
    def send_otp_via_email(mailaddress):
        otp = random.randint(1000, 9999)
        user = User.objects.get(email=mailaddress)
        username = user.name

        html_content = render_to_string(
            "otp_template.html", {"otp": otp, "user": username})
        text_content = strip_tags(html_content)
        email = EmailMultiAlternatives(
            "EDUMATE PASSWORD RESET",
            text_content,
            settings.EMAIL_HOST,
            [mailaddress]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        otprelation = OTP.objects.get(user = user)
        otprelation.otp = otp
        otprelation.otp_created_at = timezone.now()
        otprelation.isexpired = False
        otprelation.save()

    def send_credentials_via_email(userID, password, name, mailaddress, designation):
        html_content = render_to_string("newaccount_template.html", {
                                        "user": name, "userID": userID, "password": password, "designation": designation})
        text_content = strip_tags(html_content)
        email = EmailMultiAlternatives(
            "EDUMATE ACCOUNT CREATED",
            text_content,
            settings.EMAIL_HOST,
            [mailaddress]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

    def send_otp_for_email_verification(userID, mailaddress):
        otp = random.randint(1000, 9999)
        user = User.objects.get(userID=userID)
        otprelation = OTP.objects.get(user = user)
        otprelation.otp = otp
        otprelation.otp_created_at = timezone.now()
        otprelation.isexpired = False
        otprelation.save()
        user = user.name
        html_content = render_to_string("email_verification.html", {
                                        "otp": otp, "user": user})
        text_content = strip_tags(html_content)
        email = EmailMultiAlternatives(
            "EDUMATE MAIL VERIFICATION",
            text_content,
            settings.EMAIL_HOST,
            [mailaddress]
        )

        email.attach_alternative(html_content, "text/html")
        email.send()
