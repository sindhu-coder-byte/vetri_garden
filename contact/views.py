from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
import smtplib

def contact_page(request):
    if request.method == "POST":
        name    = request.POST.get('name', '').strip()
        email   = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        full_message = f"From: {name} <{email}>\n\nMessage:\n{message}"

        try:
            send_mail(
                subject,
                full_message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )
            return render(request, 'contact/contact_success.html', {'name': name})

        except smtplib.SMTPAuthenticationError:
            messages.error(request,
                "Email delivery failed: Gmail credentials are invalid or expired. "
                "Please regenerate your App Password in your Google Account settings.")
        except Exception as e:
            messages.error(request, f"Could not send message: {e}")

    return render(request, 'contact/contact.html')
