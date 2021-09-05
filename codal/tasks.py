from celery import shared_task
import jdatetime
from requests.exceptions import RequestException
from dynamic_preferences.registries import global_preferences_registry

from codal.models import Log, Letter
from codal.utils import update, jalali_datetime_to_structured_string
from codal import processor


@shared_task()
def update():

    global_preferences = global_preferences_registry.manager()

    now = jdatetime.datetime.now()

    try:
        last_letter_datetime = Letter.objects.latest('publish_datetime').publish_datetime

        Log.objects.create(
            type=Log.TYPES.INFO,
            message="بروزرسانی گزارشات شروع شد.",
            error=""
        )
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
        global_preferences['update_from_date'] = jalali_datetime_to_structured_string(now)

    Log.objects.create(
        type=Log.TYPES.ERROR if error else Log.TYPES.SUCCESS,
        message=message,
        error=error
    )

    processor.UPDATE_TASK_ID = None
