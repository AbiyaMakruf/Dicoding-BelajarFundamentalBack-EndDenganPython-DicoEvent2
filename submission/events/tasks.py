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
        ticket__event__start_time__gte=reminder_time,
        ticket__event__start_time__lt=reminder_time + timedelta(minutes=5)
    )

    if not registrations.exists():
        app_logger.info("No registrations found for reminder window")

    for reg in registrations:
        event = reg.ticket.event
        user = reg.user
        subject = f"Reminder: {event.name}"
        message = (
            f"Halo {user.username},\n\n"
            f"Jangan lupa! Event '{event.name}' akan dimulai pada {event.start_time}."
        )

        try:
            send_mail(subject, message, None, [user.email], fail_silently=False)
            app_logger.info(
                f"Reminder sent to {user.email} for event {event.name} ({event.start_time})"
            )
        except Exception as e:
            app_logger.error(f"Failed to send reminder to {user.email}: {str(e)}")

    return f"Sent {registrations.count()} reminders"
