from django.contrib import admin
from django.contrib import messages
from django.conf.urls import url
from django.shortcuts import redirect
from django.urls import reverse
from django.db import transaction
from rangefilter.filters import DateTimeRangeFilter
from django.forms.models import BaseInlineFormSet

from codal.models import Letter, Log, Attachment, Task
from codal.utils import serialize_instance
from codal import utils, tasks


class AttachmentInline(admin.TabularInline):
    model = Attachment
    exclude = ('url', )


class LetterAdmin(admin.ModelAdmin):
    list_display = ['title', 'symbol', 'status']
    ordering = ['-publish_datetime']
    search_fields = ['symbol', 'title', 'tracing_no']
    list_filter = ['status', ('publish_datetime', DateTimeRangeFilter), ]
    actions = ['download']
    date_hierarchy = 'publish_datetime'
    change_list_template = 'change_list.html'
    inlines = [AttachmentInline, ]

    def get_rangefilter_publish_datetime_title(self, request, field_path):
        return 'Publish DateTime'

    def download(self, request, queryset):
        serialized_letters = [serialize_instance(letter) for letter in queryset
                              if letter.status == Letter.Statuses.RETRIEVED]
        transaction.on_commit(lambda: tasks.download.delay(serialized_letters))
        self.message_user(request, "{} letters scheduled to download.".format(queryset.count()), messages.SUCCESS)

    # def get_actions(self, request):
    #     actions = super().get_actions(request)
    #     if 'delete_selected' in actions:
    #         del actions['delete_selected']
    #     return actions

    def get_urls(self):
        urls = []

        regex = r'^{}/$'.format(self.update.__name__)
        view = self.admin_site.admin_view(self.update)
        urls.append(url(regex, view))

        regex = r'^{}/$'.format(self.download_all.__name__)
        view = self.admin_site.admin_view(self.download_all)
        urls.append(url(regex, view))

        return urls + super(LetterAdmin, self).get_urls()

    def update(self, request):
        if Task.objects.filter(task_type=Task.TaskTypes.UPDATE, status=Task.Statuses.RUNNING).exists():
            self.message_user(request, "There Is A Update Task Already.", messages.ERROR)
            return redirect(reverse('admin:codal_letter_changelist'))
        Task.objects.create(
            type=Task.Types.RUNTIME,
            task_type=Task.TaskTypes.UPDATE,
            status=Task.Statuses.RUNNING,
        )
        transaction.on_commit(lambda: tasks.update.delay())
        self.message_user(request, "Update Scheduled.", messages.INFO)
        return redirect(reverse('admin:codal_letter_changelist'))

    def download_all(self, request):
        if Task.objects.filter(task_type=Task.TaskTypes.DOWNLOAD, status=Task.Statuses.RUNNING).exists():
            self.message_user(request, "There Is A Download Task Already.", messages.ERROR)
            return redirect(reverse('admin:codal_letter_changelist'))
        Task.objects.create(
            type=Task.Types.RUNTIME,
            task_type=Task.TaskTypes.DOWNLOAD,
            status=Task.Statuses.RUNNING,
        )
        transaction.on_commit(lambda: tasks.download_retrieved_letter.delay())
        self.message_user(request, "Download Retrieved Letters Scheduled.", messages.INFO)
        return redirect(reverse('admin:codal_letter_changelist'))

    def changelist_view(self, request, extra_context=None):
        links = []

        links.append(
            {
                'label': 'Update',
                'href': self.update.__name__,
            }
        )
        links.append(
            {
                'label': "Download All",
                'href': self.download_all.__name__,
            }
        )

        extra_context = extra_context or {}
        extra_context['extra_links'] = links

        return super(LetterAdmin, self).changelist_view(
            request, extra_context=extra_context,
        )


class LogAdmin(admin.ModelAdmin):
    list_display = ['message', 'created', 'type']
    list_filter = ['type', ('created', DateTimeRangeFilter), ]
    ordering = ['-created']
    date_hierarchy = 'created'

    def get_rangefilter_created_title(self, request, field_path):
        return 'When Created'


class AttachmentAdmin(admin.ModelAdmin):
    list_display = ['letter', 'status']
    list_filter = ['status', ('created', DateTimeRangeFilter), ]
    date_hierarchy = 'created'
    ordering = ['-created']

    def get_rangefilter_created_title(self, request, field_path):
        return 'When Created'


class TaskAdmin(admin.ModelAdmin):
    list_display = ['type', 'task_type', 'status', 'created', 'end']
    list_filter = ['status', 'task_type', 'type', ('created', DateTimeRangeFilter),]
    date_hierarchy = 'created'
    ordering = ['-created']

    def get_rangefilter_created_title(self, request, field_path):
        return 'When Created'

    def delete_queryset(self, request, queryset):
        queryset.exclude(status=Task.Statuses.RUNNING).delete()


admin.site.site_header = "Codal Administration"
admin.site.site_title = "Codal Admin"
admin.site.index_title = "Codal Admin"
admin.site.register(Letter, LetterAdmin)
admin.site.register(Log, LogAdmin)
admin.site.register(Attachment, AttachmentAdmin)
admin.site.register(Task, TaskAdmin)


# TODO Add Specific User
# TODO Handle Permissions
# TODO Unused Task Delete Action
# TODO Disable Letter Deletion
# TODO Download Each Part Of Letter Action
# TODO Use Jalali DateTime Filtering