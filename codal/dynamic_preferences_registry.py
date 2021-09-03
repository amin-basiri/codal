from dynamic_preferences.types import StringPreference
from dynamic_preferences.registries import global_preferences_registry


@global_preferences_registry.register
class UpdateFromDatetime(StringPreference):
    name = 'update_from_datetime'
    default = ""
    required = False

