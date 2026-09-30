from django import forms

from .models import ContactMessage, CustomTripRequest


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "subject", "message", "trek"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Your name"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "your@email.com"}),
            "subject": forms.TextInput(attrs={"class": "form-control", "placeholder": "Subject"}),
            "message": forms.Textarea(attrs={"class": "form-control", "rows": 5, "placeholder": "Tell us about your trip plans..."}),
            "trek": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["trek"].required = False


class CustomTripRequestForm(forms.ModelForm):
    activities = forms.MultipleChoiceField(
        required=False, widget=forms.CheckboxSelectMultiple,
        choices=[
            ("activity_trekking", "Trekking"),
            ("activity_mountaineering", "Mountaineering"),
            ("activity_peak_climbing", "Peak Climbing"),
            ("activity_rafting", "Rafting"),
            ("activity_jungle_safari", "Jungle Safari"),
            ("activity_cultural_tour", "Cultural Tour"),
            ("activity_photography", "Photography"),
            ("activity_helicopter_tour", "Helicopter Tour"),
        ],
    )

    class Meta:
        model = CustomTripRequest
        fields = [
            "name", "email", "phone", "country", "preferred_destination", "travel_dates",
            "number_of_travelers", "trip_duration_days", "budget_usd",
            "difficulty_preference", "accommodation_preference", "message",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "country": forms.TextInput(attrs={"class": "form-control"}),
            "preferred_destination": forms.Select(attrs={"class": "form-select"}),
            "travel_dates": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Mid-March 2027"}),
            "number_of_travelers": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "trip_duration_days": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "budget_usd": forms.NumberInput(attrs={"class": "form-control", "min": 0, "step": "50"}),
            "difficulty_preference": forms.Select(attrs={"class": "form-select"}),
            "accommodation_preference": forms.Select(attrs={"class": "form-select"}),
            "message": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        chosen = set(self.cleaned_data.get("activities", []))
        for field_name, _label in self.fields["activities"].choices:
            setattr(instance, field_name, field_name in chosen)
        if commit:
            instance.save()
        return instance