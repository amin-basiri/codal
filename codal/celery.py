from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab
from dynamic_preferences.registries import global_preferences_registry

from codal import tasks

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'codal.settings')
app = Celery('codal')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    global_preferences = global_preferences_registry.manager()
    update_time = global_preferences['update_schedule']
    download_time = global_preferences['download_schedule']

    sender.add_periodic_task(
        crontab(hour=update_time.hour, minute=update_time.minute),
        tasks.update.delay()
    )

    sender.add_periodic_task(
        crontab(hour=download_time.hour, minute=download_time.minute),
        tasks.download_retrieved_letter.delay()
    )
