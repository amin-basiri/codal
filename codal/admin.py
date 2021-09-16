from django.contrib import admin
from django.contrib import messages
from django.conf.urls import url
from django.shortcuts import redirect
from django.urls import reverse
from django.db import transaction

from codal.models import Letter, Log, Attachment, Task
from codal.utils import serialize_instance
from codal import utils, tasks


class LetterAdmin(admin.ModelAdmin):
    list_display = ['title', 'symbol', 'status']
    ordering = ['publish_datetime']
    actions = ['download']
    change_list_template = 'change_list.html'

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


class AttachmentAdmin(admin.ModelAdmin):
    list_display = ['letter', 'status']


class TaskAdmin(admin.ModelAdmin):
    list_display = ['type', 'task_type', 'status', 'created', 'end']


admin.site.register(Letter, LetterAdmin)
admin.site.register(Log, LogAdmin)
admin.site.register(Attachment, AttachmentAdmin)
admin.site.register(Task, TaskAdmin)

# TODO Customize Admin Template
# TODO Modify Admin And Add Actions And Tasks
# TODO Add Specific User
# TODO Handle Permissions
# TODO Unused Task Delete Action
# TODO UPDATE Task Handle Just One Task
# TODO Download All Letters Task Handle Just One Task
# TODO Admin Refresh Button
# TODO Add Log Filters
# TODO Add Letter Filter
# TODO Add Task Filter
# TODO Add Date Time Filter For Letters
# TODO Disable Letter Deletion
# TODO Just Can Delete Done Or Erred Tasks
# TODO Download Each Part Of Letter Action
# TODO Inline Attachments For Letter
# TODO Use Jalali DateTime Filtering