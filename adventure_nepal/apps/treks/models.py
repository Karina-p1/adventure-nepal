from django.db import models
from django.db.models import Avg, Count, Q
from django.templatetags.static import static
from django.urls import reverse
from django.utils.text import slugify

from apps.accounts.models import CustomUser


def unique_slug(instance, base, max_length):
    """Return a slug unique for instance's model: 'trek', 'trek-2', 'trek-3'..."""
    slug = candidate = slugify(base)[:max_length] or "item"
    model, n = instance.__class__, 2
    while model.objects.filter(slug=candidate).exclude(pk=instance.pk).exists():
        suffix = f"-{n}"
        candidate = f"{slug[:max_length - len(suffix)]}{suffix}"
        n += 1
    return candidate


class TrekRegion(models.Model):
    """A destination. Kept as TrekRegion so existing data and fixtures stay valid."""

    class RegionType(models.TextChoices):
        TREK_REGION = "trek_region", "Trekking region"
        CITY = "city", "City"
        PARK = "park", "National park"

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    region_type = models.CharField(max_length=20, choices=RegionType.choices, default=RegionType.TREK_REGION)
    hero_image = models.ImageField(upload_to="destinations/", blank=True, null=True)
    overview = models.TextField(blank=True)
    best_time_to_visit = models.CharField(max_length=200, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    meta_description = models.CharField(max_length=160, blank=True)
    order = models.PositiveSmallIntegerField(default=0, help_text="Lower numbers appear first")

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "destination"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.name, 120)
        super().save(*args, **kwargs)


class TrekQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def with_rating(self):
        """Annotate avg_rating and approved_review_count in one query."""
        approved = Q(reviews__is_approved=True)
        return self.annotate(
            avg_rating=Avg("reviews__rating", filter=approved),
            approved_review_count=Count("reviews", filter=approved),
        )


class Trek(models.Model):
    class Category(models.TextChoices):
        TREKKING = "trekking", "Trekking"
        TOUR = "tour", "Tour"
        SIGHTSEEING = "sightseeing", "Sightseeing"
        CLIMBING = "climbing", "Climbing"
        CULTURAL = "cultural", "Cultural tour"
        SAFARI = "safari", "Jungle safari"
        RAFTING = "rafting", "Rafting"
        ADVENTURE = "adventure", "Adventure activity"

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
    meta_description = models.CharField(max_length=160, blank=True, help_text="Search-result summary (optional)")

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
    is_popular = models.BooleanField(default=False, help_text="Show in the homepage 'Popular treks' carousel")
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = TrekQuerySet.as_manager()

    class Meta:
        ordering = ["-is_featured", "title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.title, 220)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("treks:detail", kwargs={"slug": self.slug})

    @property
    def cover_url(self):
        return self.cover_image.url if self.cover_image else static("img/placeholder-trek.svg")

    @property
    def has_discount(self):
        return bool(self.discount_price_usd and self.discount_price_usd < self.price_usd)

    @property
    def display_price(self):
        # Fixed: previously a discount HIGHER than the price was charged.
        return self.discount_price_usd if self.has_discount else self.price_usd

    @property
    def average_rating(self):
        if hasattr(self, "avg_rating"):
            value = self.avg_rating
        else:
            value = self.reviews.filter(is_approved=True).aggregate(a=Avg("rating"))["a"]
        return round(value, 1) if value is not None else None

    @property
    def review_count(self):
        if hasattr(self, "approved_review_count"):
            return self.approved_review_count
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