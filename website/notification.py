from django.utils import timezone
from .models import WateringReminder, ScheduleReminder
from webpush import send_user_notification


def check_reminders():

    now = timezone.now()

    watering_reminders = WateringReminder.objects.filter(
        watering_date=now.date(),
        watering_time__hour=now.hour,
        watering_time__minute=now.minute,
        is_watered=False
    )

    for reminder in watering_reminders:

        payload = {
            "head": "Watering Reminder 🌱",
            "body": f"Time to water {reminder.plant_name}"
        }

        send_user_notification(
            user=reminder.user,
            payload=payload
        )


    schedule_reminders = ScheduleReminder.objects.filter(
        schedule_date=now.date(),
        schedule_time__hour=now.hour,
        schedule_time__minute=now.minute,
        is_done=False
    )

    for reminder in schedule_reminders:

        payload = {
            "head": "Plant Care Reminder 🌿",
            "body": f"{reminder.task} for {reminder.plant_name}"
        }

        send_user_notification(
            user=reminder.user,
            payload=payload
        )