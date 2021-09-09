from django.contrib import admin
from codal.models import Letter, Log, Attachment


class LetterAdmin(admin.ModelAdmin):
    list_display = ['title', 'symbol', 'status']


class LogAdmin(admin.ModelAdmin):
    list_display = ['message', 'type']


class AttachmentAdmin(admin.ModelAdmin):
    list_display = ['letter', ]


admin.site.register(Letter, LetterAdmin)
admin.site.register(Log, LogAdmin)
admin.site.register(Attachment, AttachmentAdmin)

# TODO Modify Admin And Add Actions And Tasks
# TODO Add Specific User
# TODO Unused Task Delete Action
# TODO UPDATE Task
# TODO Download All Letters Task
# TODO Download Letter Action
# TODO Admin Refresh Button
# TODO Add Log Filters
# TODO Add Letter Filter
# TODO Add Task Filter
# TODO Add Date Time Filter For Letters
# TODO Disable Letter Deletion
# TODO Just Can Delete Done Or Erred Tasks
# TODO Download Each Part Of Letter Action