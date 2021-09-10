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
    required = True


@global_preferences_registry.register
class ReplaceArabicWordFolder(BooleanPreference):
    name = 'replace_arabic_word_folder'
    default = True
    required = True


@global_preferences_registry.register
class ReplaceArabicNumberContent(BooleanPreference):
    name = 'replace_arabic_number_content'
    default = True
    required = True


@global_preferences_registry.register
class ReplaceArabicNumberFolder(BooleanPreference):
    name = 'replace_arabic_number_folder'
    default = True
    required = True


@global_preferences_registry.register
class DownloadContent(BooleanPreference):
    name = 'download_content'
    default = True
    required = True


@global_preferences_registry.register
class DownloadExcel(BooleanPreference):
    name = 'download_excel'
    default = True
    required = True


@global_preferences_registry.register
class DownloadPdf(BooleanPreference):
    name = 'download_pdf'
    default = True
    required = True


@global_preferences_registry.register
class DownloadAttachment(BooleanPreference):
    name = 'download_attachment'
    default = True
    required = True


@global_preferences_registry.register
class RemoveNameWord(StringPreference):
    name = 'remove_name_word'
    default = "(اصلاحیه)*خلاصه"  # Must Separate With Start(*)
    required = False


@global_preferences_registry.register
class DownloadContentPath(StringPreference):
    name = 'download_content_path'
    default = '/Symbols'
    required = True


@global_preferences_registry.register
class DownloadSchedule(TimePreference):
    name = 'download_schedule'
    default = datetime.time(15, 0, 0)
    required = False


@global_preferences_registry.register
class UpdateSchedule(TimePreference):
    name = 'update_schedule'
    default = datetime.time(14, 0, 0)
    required = False
