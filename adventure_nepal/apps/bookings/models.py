from django.db import models
from django.conf import settings
from apps.treks.models import Trek


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"
        COMPLETED = "completed", "Completed"

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings"
    )
    trek = models.ForeignKey(Trek, on_delete=models.CASCADE, related_name="bookings")

    trek_date = models.DateField(help_text="Preferred start date")
    number_of_people = models.PositiveIntegerField(default=1)
    special_requests = models.TextField(blank=True)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    total_price_usd = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.customer} — {self.trek.title} ({self.trek_date})"

    def save(self, *args, **kwargs):
        if not self.total_price_usd:
            self.total_price_usd = self.trek.display_price * self.number_of_people
        super().save(*args, **kwargs)