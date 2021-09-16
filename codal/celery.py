import os
from celery.schedules import crontab
from django.conf import settings
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'codal.settings')

app = Celery('codal')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


app.conf.beat_schedule = {
    'update_letters': {
        'task': 'codal.tasks.scheduled_update',
        'schedule': crontab(hour=settings.UPDATE_TASK_HOUR, minute=settings.UPDATE_TASK_MINUTE),
        'args': (),
    },
    'download_letters': {
        'task': 'codal.tasks.scheduled_download',
        'schedule': crontab(hour=settings.DOWNLOAD_TASK_HOUR, minute=settings.DOWNLOAD_TASK_MINUTE),
        'args': (),
    },
}
