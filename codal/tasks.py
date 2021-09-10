from celery import shared_task
import jdatetime
from requests.exceptions import RequestException
from dynamic_preferences.registries import global_preferences_registry
from django.utils import timezone

from codal.models import Log, Letter, Task, Attachment
from codal import utils
from codal import processor


@shared_task()
def update():
    global_preferences = global_preferences_registry.manager()

    now = timezone.now()

    try:
        last_letter_datetime = Letter.objects.latest('publish_datetime').publish_datetime
    except Letter.DoesNotExist:
        last_letter_datetime = None

    Log.objects.create(
        type=Log.Types.INFO,
        message="بروزرسانی گزارشات شروع شد.",
        error=""
    )

    try:
        utils.update()
    except RequestException as e:
        message = "به دلیل اختلال در اینترنت , به روز رسانی با خطا مواجه شد"
        error = str(e)
    except Exception as e:
        message = "به روزرسانی با خطای نامعلومی مواجه شد"
        error = str(e)
    else:
        message = "به روز رسانی با موفقیت انجام شد"
        error = ""
        global_preferences['update_from_date'] = utils.jalali_datetime_to_structured_string(
            jdatetime.datetime.fromgregorian(now)
        )

    Log.objects.create(
        type=Log.Types.ERROR if error else Log.Types.SUCCESS,
        message=message,
        error=error
    )

    if error:
        Task.objects.get(
            status=Task.Statuses.RUNNING,
            type=Task.Types.RUNTIME,
            task_type=Task.TaskTypes.UPDATE,
            celery_id=processor.UPDATE_TASK_ID,
        ).set_erred(error)
    else:
        Task.objects.get(
            status=Task.Statuses.RUNNING,
            type=Task.Types.RUNTIME,
            task_type=Task.TaskTypes.UPDATE,
            celery_id=processor.UPDATE_TASK_ID
        ).set_done()

    processor.UPDATE_TASK_ID = None


@shared_task
def download_retrieved_letter():
    Log.objects.create(
        type=Log.Types.INFO,
        message="دانلود گزارشات دانلود نشده شروع شد.",
        error=""
    )

    un_downloaded_letters = Letter.objects.filter(status=Letter.Statuses.RETRIEVED)

    global_preferences = global_preferences_registry.manager()
    download_pdf_pref = global_preferences['download_pdf']
    download_content_pref = global_preferences['download_content']
    download_excel_pref = global_preferences['download_excel']
    download_attachment_pref = global_preferences['download_attachment']

    try:
        for letter in un_downloaded_letters:
            letter.set_downloading()
            utils.download(
                letter,
                download_pdf=download_pdf_pref and letter.has_pdf,
                download_content=download_content_pref and letter.has_html,
                download_excel=download_excel_pref and letter.has_excel,
                download_attachment=download_attachment_pref and letter.has_attachment
            )
            letter.set_downloaded()
    except RequestException as e:
        message = "به دلیل اختلال در اینترنت , دانلود گزارشات دانلود نشده با خطا مواجه شد."
        error = str(e)
    except Exception as e:
        message = "دانلود گزارشات دانلود نشده با خطای نامعلومی مواجه شد"
        error = str(e)
    else:
        message = "دانلود گزارشات دانلود نشده با موفقیت انجام شد"
        error = ""

    Log.objects.create(
        type=Log.Types.ERROR if error else Log.Types.SUCCESS,
        message=message,
        error=error
    )

    Letter.objects.filter(
        status=Letter.Statuses.DOWNLOADING
    ).update(status=Letter.Statuses.RETRIEVED)

    Attachment.objects.filter(
        status=Attachment.Statuses.DOWNLOADING
    ).update(status=Attachment.Statuses.RETRIEVED)

    if error:
        Task.objects.get(
            status=Task.Statuses.RUNNING,
            type=Task.Types.RUNTIME,
            task_type=Task.TaskTypes.DOWNLOAD,
            celery_id=processor.DOWNLOAD_TASK_ID,
        ).set_erred(error)
    else:
        Task.objects.get(
            status=Task.Statuses.RUNNING,
            type=Task.Types.RUNTIME,
            task_type=Task.TaskTypes.DOWNLOAD,
            celery_id=processor.DOWNLOAD_TASK_ID
        ).set_done()

    processor.DOWNLOAD_TASK_ID = None


@shared_task
def download(serialized_letters):
    deserialized_letters = [utils.deserialize_instance(letter) for letter in serialized_letters]

    global_preferences = global_preferences_registry.manager()
    download_pdf_pref = global_preferences['download_pdf']
    download_content_pref = global_preferences['download_content']
    download_excel_pref = global_preferences['download_excel']
    download_attachment_pref = global_preferences['download_attachment']

    for letter in deserialized_letters:
        Log.objects.create(
            type=Log.Types.INFO,
            message="دانلود گزارش با شماره پیگیری {tracing_no} شروع شد.".format(tracing_no=letter.tracing_no),
            error=""
        )

        try:
            letter.set_downloading()
            utils.download(
                letter,
                download_pdf=download_pdf_pref and letter.has_pdf,
                download_content=download_content_pref and letter.has_html,
                download_excel=download_excel_pref and letter.has_excel,
                download_attachment=download_attachment_pref and letter.has_attachment
            )
            letter.set_downloaded()
        except RequestException as e:
            message = "به دلیل اختلال در اینترنت , دانلود گزارش با شماره پیگیری {tracing_no} با خطا مواجه شد.".format(
                tracing_no=letter.tracing_no
            )
            error = str(e)
        except Exception as e:
            message = "دانلود گزارش با شماره پیگیری {tracing_no} با خطای نامعلومی مواجه شد."
            error = str(e)
        else:
            message = "دانلود گزارش با شماره پیگیری {tracing_no} با موفقیت انجام شد."
            error = ""

        Log.objects.create(
            type=Log.Types.ERROR if error else Log.Types.SUCCESS,
            message=message,
            error=error
        )

        if letter.status == Letter.Statuses.DOWNLOADING:
            letter.set_retrieved()
            for attachment in letter.attachments.filter(status=Attachment.Statuses.DOWNLOADING):
                attachment.set_retrieved()
