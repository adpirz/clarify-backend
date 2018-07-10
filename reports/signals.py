from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from sis_pull.models import Staff


@receiver(post_save, sender=Staff)
def create_worksheet_if_none_for_staff(sender, instance, **kwargs):
    if not instance.worksheet_set.exists():
        worksheet_title = ""
        user = instance.user
        if user.last_name:
            worksheet_title = f"{str(instance)}'s first worksheet"
        elif user.first_name:
            worksheet_title = f"{str(user.first_name)}'s first worksheet"
        else:
            worksheet_title = f"{str(user.username)}'s first worksheet"
        instance.worksheet_set.create(staff_id=instance.id,
                                      title=worksheet_title)


@receiver(user_logged_in)
def create_worksheet_if_none_on_login(sender, request, user, **kwargs):
    # Note that "is_staff" refers to Django, and not the sis_pull Staff model
    if user.is_staff:
        return
    staff = user.staff
    if staff and not staff.worksheet_set.exists():
        staff.worksheet_set.create(staff_id=staff.id,
                                   title=f"{str(staff)}'s first worksheet")