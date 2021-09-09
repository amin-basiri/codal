from django.db import models, transaction
from model_utils.models import TimeStampedModel


class StatusMixin(models.Model):
    class Meta:
        abstract = True

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

    def set_retrieved(self):
        self.status = self.STATUSES.RETRIEVED
        self.save()

    def set_downloading(self):
        self.status = self.STATUSES.DOWNLOADING
        self.save()

    def set_downloaded(self):
        self.status = self.STATUSES.DOWNLOADED
        self.save()


class Letter(TimeStampedModel, StatusMixin):

    attachment_url = models.CharField(max_length=500, default="", null=True)

    company_name = models.CharField(max_length=100)

    excel_url = models.CharField(max_length=500, default="", null=True)

    excel = models.FileField(upload_to='excels/', default=None, null=True)

    has_attachment = models.BooleanField(default=False)

    has_excel = models.BooleanField(default=False)

    has_html = models.BooleanField(default=True)

    has_pdf = models.BooleanField(default=True)

    pdf = models.FileField(upload_to='pdfs/', default=None, null=True)

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

    def __str__(self):
        return self.title


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


class Attachment(TimeStampedModel, StatusMixin):

    letter = models.ForeignKey(Letter, on_delete=models.CASCADE, related_name='attachments')

    file = models.FileField(upload_to='attachments/', null=True, blank=True)

    url = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.letter.title
