from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.accounts.models import CustomUser, CustomerProfile, GuideProfile


@receiver(post_save, sender=CustomUser)
def create_role_profile(sender, instance, created, **kwargs):
    if instance.role == CustomUser.Role.CUSTOMER:
        CustomerProfile.objects.get_or_create(user=instance)
        GuideProfile.objects.filter(user=instance).delete()
    elif instance.role == CustomUser.Role.GUIDE:
        GuideProfile.objects.get_or_create(user=instance)
        CustomerProfile.objects.filter(user=instance).delete()