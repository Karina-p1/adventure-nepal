from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.accounts.models import CustomUser, CustomerProfile, GuideProfile


@receiver(post_save, sender=CustomUser)
def create_role_profile(sender, instance, created, **kwargs):
    # Create-only: never delete the other profile. Switching a user's role in admin
    # (customer <-> guide) must not silently destroy their emergency contact, bio, etc.
    # If a role change needs a fresh profile of the new type, create one explicitly in admin.
    if not created:
        return
    if instance.role == CustomUser.Role.CUSTOMER:
        CustomerProfile.objects.get_or_create(user=instance)
    elif instance.role == CustomUser.Role.GUIDE:
        GuideProfile.objects.get_or_create(user=instance)