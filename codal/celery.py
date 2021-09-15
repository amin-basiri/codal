import os

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


# @app.on_after_fork.connect
# def setup_periodic_tasks(sender, **kwargs):
#     global_preferences = global_preferences_registry.manager()
#     update_time = global_preferences['update_schedule']
#     download_time = global_preferences['download_schedule']
#
#     sender.add_periodic_task(
#         crontab(hour=update_time.hour, minute=update_time.minute),
#         update.s()  # TODO Add Task To Log And Handle Task
#     )
#
#     sender.add_periodic_task(
#         crontab(hour=download_time.hour, minute=download_time.minute),
#         download_retrieved_letter.s()  # TODO Add Task To Log And Handle Task
#     )
