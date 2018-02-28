


from .models import AdminNotifier, UserNotifier, AbstractNotifier


def notify_user(template, to_email, from_email=None, subject=None, context=None):
    notifier = UserNotifier(
        template=template,
        to_email=to_email,
        from_email=from_email,
        subject=subject,
        context=context
    )
    return notifier.notify_user()


def notify_admin(template, from_email=None, subject=None, context=None):
    notifier = AdminNotifier(
        template=template,
        from_email=from_email,
        subject=subject,
        context=context
    )
    return notifier.notify_subs()


def send_mail(text, to_email, from_email, subject):
    return AbstractNotifier.send_message_via_api(text, to_email, from_email, subject)