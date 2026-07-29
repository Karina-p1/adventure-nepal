from django.db import models
from django.utils.text import slugify
from django.urls import reverse

from apps.accounts.models import CustomUser


class TrekRegion(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Trek(models.Model):
    class Category(models.TextChoices):
        TREKKING = "trekking", "Trekking"
        TOUR = "tour", "Tour"
        SIGHTSEEING = "sightseeing", "Sightseeing"
        CLIMBING = "climbing", "Climbing"

    category = models.CharField(max_length=20, choices=Category.choices, default=Category.TREKKING)
    class Difficulty(models.TextChoices):
        EASY = "easy", "Easy"
        MODERATE = "moderate", "Moderate"
        DIFFICULT = "difficult", "Difficult"
        STRENUOUS = "strenuous", "Strenuous"

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    region = models.ForeignKey(TrekRegion, on_delete=models.SET_NULL, null=True, related_name="treks")
    guide = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
        limit_choices_to={"role": CustomUser.Role.GUIDE}, related_name="treks_guided"
    )

    short_description = models.CharField(max_length=300)
    description = models.TextField()

    duration_days = models.PositiveIntegerField()
    max_altitude_m = models.PositiveIntegerField(help_text="Maximum altitude in meters")
    difficulty = models.CharField(max_length=20, choices=Difficulty.choices, default=Difficulty.MODERATE)
    group_size_min = models.PositiveIntegerField(default=2)
    group_size_max = models.PositiveIntegerField(default=12)
    best_season = models.CharField(max_length=200, blank=True, help_text="e.g. Mar-May, Sep-Nov")

    price_usd = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price_usd = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    cover_image = models.ImageField(upload_to="treks/covers/")
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_featured", "title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("treks:detail", kwargs={"slug": self.slug})

    @property
    def display_price(self):
        return self.discount_price_usd or self.price_usd

    @property
    def has_discount(self):
        return bool(self.discount_price_usd and self.discount_price_usd < self.price_usd)

    @property
    def average_rating(self):
        approved = self.reviews.filter(is_approved=True)
        if not approved.exists():
            return None
        return round(sum(r.rating for r in approved) / approved.count(), 1)

    @property
    def review_count(self):
        return self.reviews.filter(is_approved=True).count()

class TrekItineraryDay(models.Model):
    trek = models.ForeignKey(Trek, on_delete=models.CASCADE, related_name="itinerary_days")
    day_number = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField()
    altitude_m = models.PositiveIntegerField(blank=True, null=True)
    distance_km = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)

    class Meta:
        ordering = ["day_number"]
        unique_together = ("trek", "day_number")

    def __str__(self):
        return f"{self.trek.title} — Day {self.day_number}"


class TrekImage(models.Model):
    trek = models.ForeignKey(Trek, on_delete=models.CASCADE, related_name="gallery_images")
    image = models.ImageField(upload_to="treks/gallery/")
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.trek.title} image {self.order}"