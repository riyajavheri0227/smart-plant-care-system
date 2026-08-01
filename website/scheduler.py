from datetime import datetime, timedelta
import json

from apscheduler.schedulers.background import BackgroundScheduler
from pywebpush import webpush

from django.conf import settings

from .models import (
    WateringReminder,
    ScheduleReminder,
    PushSubscription,
)


def send_push_notification(user, title, body):

    subscriptions = PushSubscription.objects.filter(user=user)

    for sub in subscriptions:
        try:
            webpush(
                subscription_info={
                    "endpoint": sub.endpoint,
                    "keys": {
                        "p256dh": sub.p256dh,
                        "auth": sub.auth,
                    },
                },
                data=json.dumps({
                    "title": title,
                    "body": body,
                }),
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims={
                    "sub": "mailto:admin@example.com"
                },
            )

            print("✅ Notification sent")

        except Exception as e:
            print("❌ Push Error:", e)


def check_reminders():

    current = datetime.now()

    # Watering reminders
    watering_reminders = WateringReminder.objects.filter(is_watered=False)

    for reminder in watering_reminders:

        reminder_datetime = datetime.combine(
            reminder.watering_date,
            reminder.watering_time
        )

        if reminder_datetime <= current and not reminder.notification_sent:
            print("Watering reminder triggered:", reminder.plant_name)
            print("Sending notification...")
            send_push_notification(
                reminder.user,
                "💧 Watering Reminder",
                f"Time to water {reminder.plant_name}"
            )

            if reminder.repeat == "Daily":
                reminder.watering_date += timedelta(days=1)

            elif reminder.repeat == "Weekly":
                reminder.watering_date += timedelta(days=7)

            elif reminder.repeat == "Monthly":
                reminder.watering_date += timedelta(days=30)

            else:
                reminder.is_watered = True
                

            reminder.notification_sent = True
            reminder.save()

        elif reminder_datetime > current and reminder.notification_sent:
            reminder.notification_sent = False
            reminder.save()


    # Schedule reminders
    schedule_reminders = ScheduleReminder.objects.filter(is_done=False)

    for reminder in schedule_reminders:

        reminder_datetime = datetime.combine(
            reminder.schedule_date,
            reminder.schedule_time
        )

        if reminder_datetime <= current and not reminder.notification_sent:

            send_push_notification(
                reminder.user,
                "📅 Schedule Reminder",
                f"{reminder.plant_name} - {reminder.task}"
            )

            if reminder.repeat == "Daily":
                reminder.schedule_date += timedelta(days=1)

            elif reminder.repeat == "Weekly":
                reminder.schedule_date += timedelta(days=7)

            elif reminder.repeat == "Monthly":
                reminder.schedule_date += timedelta(days=30)

            else:
                reminder.is_done = True

            reminder.notification_sent = True
            reminder.save()

        elif reminder_datetime > current and reminder.notification_sent:
            reminder.notification_sent = False
            reminder.save()


scheduler = BackgroundScheduler()

if not scheduler.running:

    scheduler.add_job(
        check_reminders,
        "interval",
        minutes=1,
        id="check_reminders",
        replace_existing=True,
    )

    scheduler.start()

print("✅ Reminder Scheduler Started")