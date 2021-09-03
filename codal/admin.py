from django.contrib import admin
from codal.models import Letter


class LetterAdmin(admin.ModelAdmin):
    list_display = ['tracing_no', 'symbol', 'status']


admin.site.register(Letter, LetterAdmin)