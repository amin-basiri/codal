from dynamic_preferences.types import StringPreference
from dynamic_preferences.registries import global_preferences_registry


@global_preferences_registry.register
class UpdateFromDate(StringPreference):
    name = 'update_from_date'
    default = ""
    required = False

