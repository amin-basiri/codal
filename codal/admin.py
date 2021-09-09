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
