from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings

def contact_page(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        # Combine message
        full_message = f"From: {name} <{email}>\n\nMessage:\n{message}"

        # Send email to admin
        send_mail(
            subject,
            full_message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.DEFAULT_FROM_EMAIL],  # admin email (you can change)
            fail_silently=False,
        )

        return render(request, 'contact/contact_success.html', {'name': name})

    return render(request, 'contact/contact.html')
