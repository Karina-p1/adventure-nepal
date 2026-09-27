from datetime import timedelta

from django import forms
from django.utils import timezone

from .models import Booking


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["full_name", "email", "phone", "country", "trek_date", "number_of_people", "special_requests"]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "country": forms.TextInput(attrs={"class": "form-control"}),
            "trek_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "number_of_people": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "special_requests": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, trek=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.trek = trek
        tomorrow = (timezone.localdate() + timedelta(days=1)).isoformat()
        self.fields["trek_date"].widget.attrs["min"] = tomorrow
        if trek:
            self.fields["number_of_people"].widget.attrs["max"] = trek.group_size_max

    def clean_trek_date(self):
        date = self.cleaned_data["trek_date"]
        if date <= timezone.localdate():
            raise forms.ValidationError("Please choose a date at least a day from now.")
        return date

    def clean_number_of_people(self):
        n = self.cleaned_data["number_of_people"]
        if n < 1:
            raise forms.ValidationError("At least 1 traveler is required.")
        if self.trek and n > self.trek.group_size_max:
            raise forms.ValidationError(f"This trek takes at most {self.trek.group_size_max} people per booking.")
        return n