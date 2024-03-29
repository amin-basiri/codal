from dynamic_preferences.types import StringPreference, BooleanPreference, TimePreference
from dynamic_preferences.registries import global_preferences_registry
import datetime


@global_preferences_registry.register
class UpdateFromDate(StringPreference):
    name = 'update_from_date'
    default = ""
    required = False


@global_preferences_registry.register
class ReplaceArabicWordContent(BooleanPreference):
    name = 'replace_arabic_word_content'
    default = True
    required = False


@global_preferences_registry.register
class ReplaceArabicWordFolder(BooleanPreference):
    name = 'replace_arabic_word_folder'
    default = True
    required = False


@global_preferences_registry.register
class ReplaceArabicNumberContent(BooleanPreference):
    name = 'replace_arabic_number_content'
    default = True
    required = False


@global_preferences_registry.register
class ReplaceArabicNumberFolder(BooleanPreference):
    name = 'replace_arabic_number_folder'
    default = True
    required = False


@global_preferences_registry.register
class DownloadContent(BooleanPreference):
    name = 'download_content'
    default = True
    required = False


@global_preferences_registry.register
class DownloadExcel(BooleanPreference):
    name = 'download_excel'
    default = True
    required = False


@global_preferences_registry.register
class DownloadPdf(BooleanPreference):
    name = 'download_pdf'
    default = True
    required = False


@global_preferences_registry.register
class DownloadAttachment(BooleanPreference):
    name = 'download_attachment'
    default = True
    required = False


@global_preferences_registry.register
class RemoveNameWord(StringPreference):
    name = 'remove_name_word'
    default = "(اصلاحیه)*خلاصه"  # Must Separate With Start(*)
    required = False


@global_preferences_registry.register
class DownloadContentPath(StringPreference):
    name = 'download_content_path'
    default = 'Symbols'
    required = False


@global_preferences_registry.register
class DownloadScheduleEnabled(BooleanPreference):
    name = 'download_schedule_enabled'
    default = False
    required = False


@global_preferences_registry.register
class UpdateScheduleEnabled(BooleanPreference):
    name = 'update_schedule_enabled'
    default = False
    required = False


@global_preferences_registry.register
class DownloadExcelPath(StringPreference):
    name = 'download_excel_path'
    default = 'excels'
    required = False


@global_preferences_registry.register
class DownloadPdfPath(StringPreference):
    name = 'download_pdf_path'
    default = 'pdfs'
    required = False


@global_preferences_registry.register
class DownloadAttachmentPath(StringPreference):
    name = 'download_attachment_path'
    default = 'attachments'
    required = False
