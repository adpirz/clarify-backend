from django.db.models.signals import post_save
from django.dispatch import receiver
from sis_pull.models import Staff


@receiver(post_save, sender=Staff)
def create_worksheet_if_none_for_staff(sender, instance, **kwargs):
    if not instance.worksheet_set.exists():
        instance.worksheet_set.create(staff_id=instance.id,
                                      title=f"{str(instance)}'s first worksheet")