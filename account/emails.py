from django.template.loader import render_to_string
from django.utils.html import strip_tags
import random
from django.utils import timezone
from . models import *
from . tasks import send_email_through_celery

class EMAIL:
    @staticmethod
    def send_otp_via_email(mailaddress):
        otp = random.randint(1000, 9999)
        user = User.objects.get(email=mailaddress)
        username = user.name

        html_content = render_to_string(
            "otp_template.html", {"otp": otp, "user": username})
        send_email_through_celery.delay("EDUMATE PASSWORD RESET", html_content, mailaddress)
        otprelation = OTP.objects.get(user=user)
        otprelation.otp = otp
        otprelation.otp_created_at = timezone.now()
        otprelation.isexpired = False
        otprelation.save()


    def send_credentials_via_email(userID, password, name, mailaddress, designation):
        html_content = render_to_string("newaccount_template.html", {
                                        "user": name, "userID": userID, "password": password, "designation": designation})
        send_email_through_celery.delay("EDUMATE ACCOUNT CREATED", html_content, mailaddress)


    def send_otp_for_email_verification(user, mailaddress):
        otp = random.randint(1000, 9999)
        otprelation = OTP.objects.get(user=user)
        otprelation.otp = otp
        otprelation.otp_created_at = timezone.now()
        otprelation.isexpired = False
        otprelation.save()
        html_content = render_to_string("email_verification.html", {
                                        "otp": otp, "user": user.name})
        send_email_through_celery.delay("EDUMATE MAIL VERIFICATION", html_content, mailaddress)