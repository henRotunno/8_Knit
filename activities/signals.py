from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from .models import Cyber


@receiver(user_logged_in)
def log_successful_login(sender, request, user, **kwargs):

    ip = request.META.get('REMOTE_ADDR')

    Cyber.objects.create(
        username=user.username,
        event_type='LOGIN_SUCCESS',
        ip_address=ip
    )


@receiver(user_logged_out)
def log_logout(sender, request, user, **kwargs):

    if user is None:
        return

    ip = request.META.get('REMOTE_ADDR')

    Cyber.objects.create(
        username=user.username,
        event_type='LOGOUT',
        ip_address=ip
    )


@receiver(user_login_failed)
def log_failed_login(sender, credentials, request, **kwargs):
    username = credentials.get('username', 'Unknown')
    ip = request.META.get('REMOTE_ADDR') if request else None

    Cyber.objects.create(
        username=username,
        event_type='LOGIN_FAILURE',
        ip_address=ip
    )