from django.contrib.auth.signals import user_logged_in

from clarify.models import CleverSession


def user_logged_in_handler(sender, request, user):
    if user.clever_id:
        CleverSession.objects.get_or_create(
            user=user,
            session_id=request.session.session_key
        )


user_logged_in.connect(user_logged_in_handler)