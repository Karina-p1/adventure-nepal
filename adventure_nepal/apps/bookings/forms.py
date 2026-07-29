from django import forms
from .models import Booking


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["trek_date", "number_of_people", "special_requests"]
        widgets = {
            "trek_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "number_of_people": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "special_requests": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }