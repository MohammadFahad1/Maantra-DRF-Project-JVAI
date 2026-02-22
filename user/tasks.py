from celery import shared_task
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives

@shared_task
def send_otp_email(email, otp):
    subject = "OTP - Reset your Maantra Password"
    from_email = settings.EMAIL_HOST_USER # Better to use DEFAULT_FROM_EMAIL
    
    context = {"otp": otp}
        
    # 1. Generate the HTML content
    html_content = render_to_string("otp_template.html", context)
    
    # 2. Create the plain-text fallback (for watches/notifications)
    text_content = strip_tags(html_content)
    
    try:
        # 3. Create the email object
        msg = EmailMultiAlternatives(
            subject, 
            text_content, 
            from_email, 
            [email]
        )
        
        # 4. Attach the HTML version - THIS is what makes it look amazing
        msg.attach_alternative(html_content, "text/html")
        
        msg.send()
        return f'Email sent to {email}'
    except Exception as e:
        return f'Error: {e}'