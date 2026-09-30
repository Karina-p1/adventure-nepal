from django.db import models


class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    trek = models.ForeignKey(
        "treks.Trek", on_delete=models.SET_NULL, null=True, blank=True, related_name="contact_messages",
        help_text="Set automatically when someone messages from a trek page.",
    )
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} — {self.subject}"


class CustomTripRequest(models.Model):
    class Difficulty(models.TextChoices):
        NO_PREFERENCE = "no_preference", "No preference"
        EASY = "easy", "Easy"
        MODERATE = "moderate", "Moderate"
        DIFFICULT = "difficult", "Difficult"
        STRENUOUS = "strenuous", "Strenuous"

    class Accommodation(models.TextChoices):
        NO_PREFERENCE = "no_preference", "No preference"
        TEAHOUSE = "teahouse", "Teahouse / lodge"
        HOTEL = "hotel", "Hotel"
        CAMPING = "camping", "Camping"
        LUXURY = "luxury", "Luxury lodge"

    class Status(models.TextChoices):
        NEW = "new", "New"
        CONTACTED = "contacted", "Contacted"
        QUOTED = "quoted", "Quoted"
        CLOSED = "closed", "Closed"

    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    country = models.CharField(max_length=80, blank=True)

    preferred_destination = models.ForeignKey(
        "treks.TrekRegion", on_delete=models.SET_NULL, null=True, blank=True, related_name="custom_trip_requests",
    )
    travel_dates = models.CharField(max_length=200, blank=True, help_text="e.g. 'Mid-March 2027' or exact dates")
    number_of_travelers = models.PositiveIntegerField(default=1)
    trip_duration_days = models.PositiveIntegerField(blank=True, null=True)
    budget_usd = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    difficulty_preference = models.CharField(max_length=20, choices=Difficulty.choices, default=Difficulty.NO_PREFERENCE)
    accommodation_preference = models.CharField(max_length=20, choices=Accommodation.choices, default=Accommodation.NO_PREFERENCE)

    activity_trekking = models.BooleanField(default=False)
    activity_mountaineering = models.BooleanField(default=False)
    activity_peak_climbing = models.BooleanField(default=False)
    activity_rafting = models.BooleanField(default=False)
    activity_jungle_safari = models.BooleanField(default=False)
    activity_cultural_tour = models.BooleanField(default=False)
    activity_photography = models.BooleanField(default=False)
    activity_helicopter_tour = models.BooleanField(default=False)

    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} — {self.get_status_display()}"

    @property
    def activities_list(self):
        labels = {
            "activity_trekking": "Trekking", "activity_mountaineering": "Mountaineering",
            "activity_peak_climbing": "Peak climbing", "activity_rafting": "Rafting",
            "activity_jungle_safari": "Jungle safari", "activity_cultural_tour": "Cultural tour",
            "activity_photography": "Photography", "activity_helicopter_tour": "Helicopter tour",
        }
        return [label for field, label in labels.items() if getattr(self, field)]