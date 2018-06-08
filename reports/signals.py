from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from sis_pull.models import Staff


@receiver(post_save, sender=Staff)
def create_worksheet_if_none_for_staff(sender, instance, **kwargs):
    if not instance.worksheet_set.exists():
        instance.worksheet_set.create(staff_id=instance.id,
                                      title=f"{str(instance)}'s first worksheet")


@receiver(user_logged_in)
def create_worksheet_if_none_on_login(sender, request, user, **kwargs):
    staff = user.staff
    if not staff.worksheet_set.exists():
        staff.worksheet_set.create(staff_id=staff.id,
                                   title=f"{str(staff)}'s first worksheet")