import os

from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.settings")

app = Celery("src")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
crontab_process_schedule_tasks_pending = crontab(
    minute="*/1") if settings.DEBUG else crontab(minute="*/5")

app.conf.beat_schedule = {
    # "_auto_choose_driver_for_booking": {
    #     "task": "src.graphql.booking.tasks._auto_choose_driver_for_booking",
    #     "schedule": crontab(minute='*/1'),
    # },
}
