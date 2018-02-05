# coding: utf-8
from django.dispatch import Signal

chaos_instance_updated = Signal(providing_args=['instance', 'user', 'data'])
chaos_instance_deleted = Signal(providing_args=['instance', 'user'])
task_status_changed = Signal(providing_args=['task', 'status', 'changes', 'user'])
