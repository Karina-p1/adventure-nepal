from django.core.cache import cache
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class SiteSettings(models.Model):
    """Single editable record: contact details and social links shown site-wide."""

    site_name = models.CharField(max_length=100, default="Adventure Nepal")
    tagline = models.CharField(max_length=200, blank=True, default="Trekking and travel across the Himalayas, guided by locals who know the trails.")
    phone = models.CharField(max_length=30, blank=True, default="+977 9800000000")
    email = models.EmailField(blank=True, default="info@adventurenepal.com")
    address = models.CharField(max_length=255, blank=True, default="Thamel, Kathmandu, Nepal")
    opening_hours = models.CharField(max_length=200, blank=True, default="Sun–Fri, 9:00–18:00 (NPT)")
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    tiktok_url = models.URLField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site settings"
        verbose_name_plural = "Site settings"

    def __str__(self):
        return "Site settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
        cache.delete("site_settings")

    @classmethod
    def load(cls):
        obj = cache.get("site_settings")
        if obj is None:
            obj, _ = cls.objects.get_or_create(pk=1)
            cache.set("site_settings", obj, 300)
        return obj


class SiteStatistic(models.Model):
    """Trust numbers shown on the homepage. Enter only figures you can back up."""

    label = models.CharField(max_length=80, help_text="e.g. Years of experience")
    value = models.CharField(max_length=20, help_text="e.g. 12 or 1,500+")
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.value} {self.label}"


class HighlightItem(models.Model):
    """Editable icon + text blocks for 'Why choose us' and 'Responsible tourism'."""

    class Section(models.TextChoices):
        WHY = "why", "Why choose us"
        RESPONSIBLE = "responsible", "Responsible tourism"

    section = models.CharField(max_length=20, choices=Section.choices)
    icon = models.CharField(max_length=40, default="bi-compass", help_text="Bootstrap Icons class, e.g. bi-compass")
    title = models.CharField(max_length=100)
    text = models.CharField(max_length=300)
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["section", "order", "id"]

    def __str__(self):
        return f"{self.get_section_display()}: {self.title}"


class Testimonial(models.Model):
    """Editorial quote (for feedback not tied to a booking review)."""

    name = models.CharField(max_length=100)
    country = models.CharField(max_length=80, blank=True)
    photo = models.ImageField(upload_to="testimonials/", blank=True, null=True)
    quote = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(5)])
    trek = models.ForeignKey("treks.Trek", on_delete=models.SET_NULL, null=True, blank=True, related_name="testimonials")
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "-created_at"]

    def __str__(self):
        return f"{self.name} ({self.country})" if self.country else self.name


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-subscribed_at"]

    def save(self, *args, **kwargs):
        self.email = self.email.strip().lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email