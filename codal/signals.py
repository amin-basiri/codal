from django.dispatch import Signal

task_done = Signal(providing_args=['task'])
