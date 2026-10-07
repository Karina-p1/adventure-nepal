import uuid

from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models.functions import Lower

from django.utils.deconstruct import deconstructible


@deconstructible
class SizedUploadTo:
    def __init__(self, folder):
        self.folder = folder

    def __call__(self, instance, filename):
        ext = filename.rsplit(".", 1)[-1].lower()
        return f"{self.folder}/{uuid.uuid4().hex}.{ext}"


def _sized_upload_to(folder):
    return SizedUploadTo(folder)


def validate_image_size(f):
    limit_mb = 3
    if f.size > limit_mb * 1024 * 1024:
        from django.core.exceptions import ValidationError
        raise ValidationError(f"Image must be under {limit_mb}MB.")


IMAGE_VALIDATORS = [FileExtensionValidator(["jpg", "jpeg", "png", "webp"]), validate_image_size]


class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        GUIDE = "guide", "Guide"
        STAFF = "staff", "Staff"
        ADMIN = "admin", "Admin"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to=_sized_upload_to("avatars"), blank=True, null=True, validators=IMAGE_VALIDATORS)
    is_email_verified = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(Lower("email"), name="accounts_useremail_ci_unique"),
        ]

    def __str__(self):
        return self.get_full_name() or self.username

def save(self, *args, **kwargs):
    self.is_staff = self.role in (
        self.Role.STAFF,
        self.Role.ADMIN,
    )

    super().save(*args, **kwargs)

    @property
    def is_customer(self):
        return self.role == self.Role.CUSTOMER

    @property
    def is_guide(self):
        return self.role == self.Role.GUIDE

    @property
    def is_staff_member(self):
        return self.role == self.Role.STAFF


class CustomerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="customer_profile")
    address = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=80, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Customer profile: {self.user}"


class GuideProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="guide_profile")
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    position = models.CharField(max_length=100, blank=True, help_text="e.g. Lead Trekking Guide")
    photo = models.ImageField(upload_to=_sized_upload_to("guides"), blank=True, null=True, validators=IMAGE_VALIDATORS,
                               help_text="Public profile photo. Falls back to the account avatar if left blank.")
    bio = models.TextField(blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    languages = models.CharField(max_length=255, blank=True, help_text="Comma-separated, e.g. English, Nepali, Hindi")
    specialization = models.CharField(max_length=255, blank=True)
    certifications = models.CharField(max_length=255, blank=True, help_text="Comma-separated. Verify before publishing.")
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    is_public = models.BooleanField(default=True, help_text="Uncheck to hide from the public guides pages")
    order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "user__first_name"]

    def __str__(self):
        return f"Guide profile: {self.user}"

def save(self, *args, **kwargs):
    self.is_staff = self.role in (
        self.Role.STAFF,
        self.Role.ADMIN,
    )

    update_fields = kwargs.get("update_fields")

    if update_fields is not None:
        update_fields = set(update_fields)
        update_fields.add("is_staff")
        kwargs["update_fields"] = update_fields

    super().save(*args, **kwargs)

    @property
    def display_photo_url(self):
        if self.photo:
            return self.photo.url
        if self.user.avatar:
            return self.user.avatar.url
        return None

    @property
    def languages_list(self):
        return [x.strip() for x in self.languages.split(",") if x.strip()]

    @property
    def certifications_list(self):
        return [x.strip() for x in self.certifications.split(",") if x.strip()]


class SavedTrip(models.Model):
    """A customer's wishlist entry."""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="saved_trips")
    trek = models.ForeignKey("treks.Trek", on_delete=models.CASCADE, related_name="saved_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [models.UniqueConstraint(fields=["user", "trek"], name="one_save_per_user_per_trek")]

    def __str__(self):
        return f"{self.user} saved {self.trek}"