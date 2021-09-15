from .models import Task
from django.utils import timezone


def set_end_to_task(sender, instance, created=False, **kwargs):
    if instance.tracker.previous('status') == Task.Statuses.RUNNING and instance.tracker.has_changed('status') and \
            instance.status in [Task.Statuses.DONE, Task.Statuses.ERRED]:
        instance.end = timezone.now()
        instance.save(update_fields=['end'])
