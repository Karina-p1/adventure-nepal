import random
import string
from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone

from apps.treks.models import Trek


def generate_reference():
    year = timezone.now().year
    for _ in range(20):
        suffix = "".join(random.choices(string.digits, k=6))
        ref = f"AN-{year}-{suffix}"
        if not Booking.objects.filter(reference=ref).exists():
            return ref
    raise RuntimeError("Could not generate a unique booking reference")


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"
        COMPLETED = "completed", "Completed"

    class PaymentStatus(models.TextChoices):
        UNPAID = "unpaid", "Unpaid"
        PARTIAL = "partial", "Partially paid"
        PAID = "paid", "Paid"
        REFUNDED = "refunded", "Refunded"

    reference = models.CharField(max_length=20, unique=True, blank=True, null=True, editable=False)

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="bookings")
    trek = models.ForeignKey(Trek, on_delete=models.PROTECT, related_name="bookings")

    # Snapshots: what was quoted at booking time, so later trek edits never rewrite history.
    trek_title = models.CharField(max_length=200, blank=True, editable=False)
    price_per_person_usd = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, editable=False)

    # Contact details for this booking (pre-filled from the profile, editable per booking).
    full_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    country = models.CharField(max_length=80, blank=True)

    trek_date = models.DateField(help_text="Preferred start date")
    number_of_people = models.PositiveIntegerField(default=1)
    special_requests = models.TextField(blank=True)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.UNPAID)
    total_price_usd = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(check=Q(number_of_people__gte=1), name="booking_at_least_one_person"),
        ]

    def __str__(self):
        return f"{self.reference or 'DRAFT'} — {self.customer} — {self.trek_title or self.trek.title}"

    def clean(self):
        errors = {}
        if self.trek_date and self.trek_date <= timezone.localdate():
            errors["trek_date"] = "Please choose a date at least a day from now."
        if self.trek_id and self.number_of_people and self.number_of_people > self.trek.group_size_max:
            errors["number_of_people"] = f"This trek takes at most {self.trek.group_size_max} people per booking."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = generate_reference()
        if not self.trek_title and self.trek_id:
            self.trek_title = self.trek.title
        if self.price_per_person_usd is None and self.trek_id:
            self.price_per_person_usd = self.trek.display_price
        if self.price_per_person_usd is not None and self.number_of_people:
            self.total_price_usd = self.price_per_person_usd * self.number_of_people
        super().save(*args, **kwargs)

    @property
    def is_cancelable(self):
        return self.status == self.Status.PENDING

    @classmethod
    def recent_duplicate_exists(cls, customer, trek, trek_date):
        """Guards against a double form-submit creating two identical pending bookings."""
        window_start = timezone.now() - timedelta(minutes=5)
        return cls.objects.filter(
            customer=customer, trek=trek, trek_date=trek_date,
            status=cls.Status.PENDING, created_at__gte=window_start,
        ).exists()