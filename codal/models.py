from django.db import models, transaction
from model_utils.models import TimeStampedModel
from model_utils import FieldTracker


class StatusMixin(models.Model):
    class Meta:
        abstract = True

    class Statuses:
        RETRIEVED = 'retrieved'
        DOWNLOADING = 'downloading'
        DOWNLOADED = 'downloaded'

        CHOICES = (
            (RETRIEVED, 'Retrieved'),
            (DOWNLOADING, 'Downloading'),
            (DOWNLOADED, 'Downloaded')
        )

    status = models.CharField(default=Statuses.RETRIEVED, max_length=20, choices=Statuses.CHOICES)

    def set_retrieved(self):
        self.status = self.Statuses.RETRIEVED
        self.save(update_fields=['status'])

    def set_downloading(self):
        self.status = self.Statuses.DOWNLOADING
        self.save(update_fields=['status'])

    def set_downloaded(self):
        self.status = self.Statuses.DOWNLOADED
        self.save(update_fields=['status'])


class ErrorMixin(models.Model):
    class Meta:
        abstract = True

    error = models.CharField(default="", null=True, max_length=500)


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

    @property
    def attachment_count(self):
        return self.attachments.count()


class Log(TimeStampedModel, ErrorMixin):

    class Types:
        INFO = 'info'
        SUCCESS = 'success'
        ERROR = 'error'

        CHOICES = (
            (INFO, 'Info'),
            (SUCCESS, 'Success'),
            (ERROR, 'Error')
        )

    type = models.CharField(default=Types.INFO, max_length=10, choices=Types.CHOICES)

    message = models.CharField(default="", null=True, max_length=100)


class Attachment(TimeStampedModel, StatusMixin):

    letter = models.ForeignKey(Letter, on_delete=models.CASCADE, related_name='attachments')

    file = models.FileField(upload_to='attachments/', null=True, blank=True)

    url = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.letter.title


class Task(TimeStampedModel, ErrorMixin):
    class TaskTypes:
        DOWNLOAD = 'download'
        UPDATE = 'update'

        CHOICES = (
            (DOWNLOAD, 'Download'),
            (UPDATE, 'Update'),
        )

    class Statuses:
        CREATED = 'created'
        RUNNING = 'running'
        DONE = 'done'
        ERRED = 'erred'

        CHOICES = (
            (CREATED, 'Created'),
            (RUNNING, 'Running'),
            (DONE, 'Done'),
            (ERRED, 'Erred')
        )

    class Types:
        RUNTIME = 'runtime'
        SCHEDULED = 'scheduled'

        CHOICES = (
            (RUNTIME, 'Runtime'),
            (SCHEDULED, 'Scheduled')
        )

    task_type = models.CharField(default=TaskTypes.UPDATE, max_length=30, choices=TaskTypes.CHOICES)

    type = models.CharField(default=Types.RUNTIME, max_length=30, choices=Types.CHOICES)

    status = models.CharField(default=Statuses.CREATED, max_length=30, choices=Statuses.CHOICES)

    celery_id = models.IntegerField(default=0, null=True)

    end = models.DateTimeField(null=True)

    tracker = FieldTracker()

    def set_erred(self):
        self.status = self.Statuses.ERRED
        self.save(update_fields=['status'])

    def set_running(self):
        self.status = self.Statuses.RUNNING
        self.save(update_fields=['status'])

    def set_done(self):
        self.status = self.Statuses.DONE
        self.save(update_fields=['status'])


