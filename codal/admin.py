from django.contrib import admin
from django.contrib import messages

from codal.models import Letter, Log, Attachment
from codal.utils import serialize_instance
from codal import utils, tasks


class LetterAdmin(admin.ModelAdmin):
    list_display = ['title', 'symbol', 'status']
    ordering = ['publish_datetime']
    actions = ['download']

    def download(self, request, queryset):
        serialized_letters = [serialize_instance(letter) for letter in queryset
                              if letter.status == Letter.Statuses.RETRIEVED]

        tasks.download.delay(serialized_letters)
        self.message_user(request, "{} letters scheduled to download.".format(queryset.count()), messages.SUCCESS)

        # def get_actions(self, request):
        #     actions = super().get_actions(request)
        #     if 'delete_selected' in actions:
        #         del actions['delete_selected']
        #     return actions


class LogAdmin(admin.ModelAdmin):
    list_display = ['message', 'type']


class AttachmentAdmin(admin.ModelAdmin):
    list_display = ['letter', ]


admin.site.register(Letter, LetterAdmin)
admin.site.register(Log, LogAdmin)
admin.site.register(Attachment, AttachmentAdmin)

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