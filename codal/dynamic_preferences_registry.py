from dynamic_preferences.types import DateTimePreference
from dynamic_preferences.registries import global_preferences_registry


class UpdateFromDatetime(DateTimePreference):
    name = 'update_from_datetime'
    required = False

