from django.db import models, transaction
from model_utils.models import TimeStampedModel


class Letter(TimeStampedModel):

    class STATUSES:
        RETRIEVED = 'retrieved'
        DOWNLOADING = 'downloading'
        DOWNLOADED = 'downloaded'

        CHOICES = (
            (RETRIEVED, 'Retrieved'),
            (DOWNLOADING, 'Downloading'),
            (DOWNLOADED, 'Downloaded')
        )

    status = models.CharField(default=STATUSES.RETRIEVED, max_length=20, choices=STATUSES.CHOICES)

    attachment_url = models.CharField(max_length=500, default="", null=True)

    attachment = models.FileField(upload_to='attachments/', default=None, null=True)

    company_name = models.CharField(max_length=100)

    excel_url = models.CharField(max_length=500, default="", null=True)

    excel = models.FileField(upload_to='excels/', default=None, null=True)

    has_attachment = models.BooleanField(default=False)

    has_excel = models.BooleanField(default=False)

    has_html = models.BooleanField(default=True)

    has_pdf = models.BooleanField(default=True)

    has_xbrl = models.BooleanField(default=False)

    is_estimate = models.BooleanField(default=False)

    code = models.CharField(max_length=50, default="", null=True)

    pdf_url = models.CharField(max_length=500, default="", null=True)

    publish_datetime = models.DateTimeField()

    sent_datetime = models.DateTimeField()

    symbol = models.CharField(max_length=100)

    # tedan_url = models.CharField(max_length=500, default="", null=True)

    title = models.CharField(max_length=500)

    tracing_no = models.IntegerField(unique=True, editable=False)

    under_supervision = models.BooleanField(default=False)

    url = models.CharField(max_length=500, default="", null=True)

    xbrl_url = models.CharField(max_length=500, default="", null=True)


class Log(TimeStampedModel):

    class TYPES:
        INFO = 'info'
        SUCCESS = 'success'
        ERROR = 'error'

        CHOICES = (
            (INFO, 'Info'),
            (SUCCESS, 'Success'),
            (ERROR, 'Error')
        )

    type = models.CharField(default=TYPES.INFO, max_length=10, choices=TYPES.CHOICES)

    message = models.CharField(default="", null=True, max_length=100)

    error = models.CharField(default="", null=True, max_length=500)
