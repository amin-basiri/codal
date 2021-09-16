from .models import Task
from django.utils import timezone


def set_end_to_task(sender, task, **kwargs):
    task.end = timezone.now()
    task.save(update_fields=['end'])
