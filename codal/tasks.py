from celery import shared_task
from codal.models import Log, Letter
from codal.utils import update
from codal import runtime_data
from requests.exceptions import RequestException


@shared_task()
def update():
    try:
        last_letter_datetime = Letter.objects.latest('publish_datetime').publish_datetime
        # TODO Add Logger
        # TODO Add Current Date
    except Letter.DoesNotExist:
        last_letter_datetime = None

    try:
        update(from_datetime=last_letter_datetime)
    except RequestException as e:
        message = "به دلیل اختلال در اینترنت , به روز رسانی با خطا مواجه شد"
        error = str(e)
    except Exception as e:
        message = "به روزرسانی با خطای نامعلومی مواجه شد"
        error = str(e)
    else:
        message = "به روز رسانی با موفقیت انجام شد"
        error = ""

    Log.objects.create(
        type=Log.TYPES.ERROR if error else Log.TYPES.SUCCESS,
        message=message,
        error=error
    )

    runtime_data.UPDATE_TASK_ID = None
