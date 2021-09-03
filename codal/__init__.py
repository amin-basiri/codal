from __future__ import absolute_import

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app


class RuntimeData:
    DOWNLOAD_TASK_ID = None
    UPDATE_TASK_ID = None


runtime_data = RuntimeData()
