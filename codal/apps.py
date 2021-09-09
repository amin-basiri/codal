from django.apps import AppConfig
from django.db.models import signals


class CodalConfig(AppConfig):
    name = 'codal'
    verbose_name = 'Codal'

    def ready(self):
        from . import models, handlers

        signals.post_save.connect(
            handlers.set_end_to_task,
            sender=models.Task,
            dispatch_uid='codal.set_end_to_task',
        )