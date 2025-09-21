from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from .models import Registration
from DicoEvent.logging_config import app_logger

@shared_task
def send_event_reminders():
    now = timezone.now()
    reminder_time = now + timedelta(hours=2)

    registrations = Registration.objects.filter(
        ticket__event__start_time__range=(reminder_time - timedelta(minutes=5), reminder_time + timedelta(minutes=5))
    )

    try:
        for reg in registrations:
            event = reg.ticket.event
            user = reg.user
            subject = f"Reminder: {event.name}"
            message = f"Halo {user.username},\n\nJangan lupa! Event '{event.name}' akan dimulai pada {event.start_time}."
            send_mail(subject, message, None, [user.email])
            send_mail(subject, message, None, [user.email])
            app_logger.info(f"Sent reminder to {user.email} for event {event.name}")
    except Exception as e:
        app_logger.error(f"Error sending reminders: {str(e)}")
        raise
