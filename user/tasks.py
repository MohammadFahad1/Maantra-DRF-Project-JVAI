from celery import shared_task
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail

@shared_task
def send_otp_email(email, otp):
    subject = "Reset your Maantra Password"
    from_email = settings.EMAIL_HOST_USER
    
    context = {
        "otp": otp
    }
        
    html_content = render_to_string("otp_template.html", context)
    message = strip_tags(html_content)
    
    if subject and from_email and email:
        try:
            send_mail(subject, message, from_email, [email])
            context['result'] = 'Email sent successfully'
        except Exception as e:
            context['result'] = f'Error sending email: {e}'