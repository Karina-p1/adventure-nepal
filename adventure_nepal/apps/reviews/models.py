from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

from apps.treks.models import Trek
from apps.bookings.models import Booking


class Review(models.Model):
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews"
    )
    trek = models.ForeignKey(Trek, on_delete=models.CASCADE, related_name="reviews")
    booking = models.OneToOneField(
        Booking, on_delete=models.CASCADE, related_name="review", null=True, blank=True
    )

    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=150, blank=True)
    comment = models.TextField()

    is_approved = models.BooleanField(default=True, help_text="Uncheck to hide from public trek page")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["customer", "trek"], name="one_review_per_customer_per_trek")
        ]

    def __str__(self):
        return f"{self.customer} — {self.trek.title} ({self.rating}★)"