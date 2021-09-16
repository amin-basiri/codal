from celery import shared_task
from codal.celery import app
from celery.schedules import crontab
import jdatetime
from requests.exceptions import RequestException
from dynamic_preferences.registries import global_preferences_registry
from django.utils import timezone
import logging
from django.db import transaction
from django.conf import settings

from codal.models import Log, Letter, Task, Attachment
from codal import utils

logger = logging.getLogger(__name__)


@shared_task
def update():
    global_preferences = global_preferences_registry.manager()

    now = timezone.now()

    Log.objects.create(
        type=Log.Types.INFO,
        message="بروزرسانی گزارشات شروع شد",
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
            jdatetime.datetime.fromgregorian(year=now.year, month=now.month, day=now.day)
        )

    Log.objects.create(
        type=Log.Types.ERROR if error else Log.Types.SUCCESS,
        message=message,
        error=error
    )

    utils.handle_task_complete(error, Task.TaskTypes.UPDATE)


@shared_task
def download_retrieved_letter():
    Log.objects.create(
        type=Log.Types.INFO,
        message="دانلود گزارشات دانلود نشده شروع شد",
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
        message = "به دلیل اختلال در اینترنت , دانلود گزارشات دانلود نشده با خطا مواجه شد"
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

    utils.handle_task_complete(error, Task.TaskTypes.DOWNLOAD)


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
            message="دانلود گزارش با شماره پیگیری {tracing_no} شروع شد".format(tracing_no=letter.tracing_no),
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
            message = "به دلیل اختلال در اینترنت , دانلود گزارش با شماره پیگیری {tracing_no} با خطا مواجه شد".format(
                tracing_no=letter.tracing_no
            )
            error = str(e)
        except Exception as e:
            message = "دانلود گزارش با شماره پیگیری {tracing_no} با خطای نامعلومی مواجه شد".format(
                tracing_no=letter.tracing_no
            )
            error = str(e)
        else:
            message = "دانلود گزارش با شماره پیگیری {tracing_no} با موفقیت انجام شد".format(
                tracing_no=letter.tracing_no
            )
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


@shared_task
def scheduled_update():
    if Task.objects.filter(task_type=Task.TaskTypes.UPDATE, status=Task.Statuses.RUNNING).exists():
        return

    Task.objects.create(
        type=Task.Types.SCHEDULED,
        task_type=Task.TaskTypes.UPDATE,
        status=Task.Statuses.RUNNING,
    )

    transaction.on_commit(lambda: update.delay())


@shared_task
def scheduled_download():
    if Task.objects.filter(task_type=Task.TaskTypes.DOWNLOAD, status=Task.Statuses.RUNNING).exists():
        return

    Task.objects.create(
        type=Task.Types.SCHEDULED,
        task_type=Task.TaskTypes.DOWNLOAD,
        status=Task.Statuses.RUNNING,
    )

    transaction.on_commit(lambda: download_retrieved_letter.delay())
