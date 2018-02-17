from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
# from commons.notifications.utils import (
#     send_notification_to_user,
#     get_registered_devices,
#     get_badge_count
# )
from django.db.models.signals import post_save


class Message(models.Model):
    """
    Base class for storing Messages.
    This messages are from chats between users
    and agent.
    """
    message_text = models.TextField(null=True, blank=True)
    sender = models.ForeignKey(
            User, related_name='sender_messages', verbose_name="sender")
    receiver = models.ForeignKey(
            User, related_name='reciever_messages', verbose_name="reciever")
    room_id = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    from_user_read = models.BooleanField(default=True)
    to_user_read = models.BooleanField(default=False)
    from_user_delete = models.BooleanField(default=False)
    to_user_delete = models.BooleanField(default=False)

    class Meta:
        db_table = 'message'
