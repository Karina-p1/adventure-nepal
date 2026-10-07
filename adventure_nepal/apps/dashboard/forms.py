from django import forms
from django.forms import inlineformset_factory

from apps.accounts.models import CustomUser
from apps.bookings.models import Booking
from apps.treks.models import (
    Trek,
    TrekImage,
    TrekItineraryDay,
    TrekRegion,
    TripFAQ,
    TripHighlight,
    TripInclusion,
)


# ============================================================
# BOOKING
# ============================================================

class BookingPaymentForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["payment_status"]
        widgets = {
            "payment_status": forms.Select(
                attrs={"class": "form-select"}
            ),
        }


# ============================================================
# DESTINATION
# ============================================================

class DestinationForm(forms.ModelForm):
    class Meta:
        model = TrekRegion

        fields = [
            "name",
            "region_type",
            "hero_image",
            "description",
            "overview",
            "best_time_to_visit",
            "latitude",
            "longitude",
            "meta_description",
            "order",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "region_type": forms.Select(
                attrs={"class": "form-select"}
            ),

            "hero_image": forms.ClearableFileInput(
                attrs={"class": "form-control"}
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                }
            ),

            "overview": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                }
            ),

            "best_time_to_visit": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. March–May, September–November",
                }
            ),

            "latitude": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.000001",
                }
            ),

            "longitude": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.000001",
                }
            ),

            "meta_description": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "maxlength": 160,
                }
            ),

            "order": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                }
            ),
        }


# ============================================================
# TREK
# ============================================================

class TrekForm(forms.ModelForm):
    class Meta:
        model = Trek

        fields = [
            "title",
            "category",
            "region",
            "guides",

            "short_description",
            "description",
            "meta_description",

            "duration_days",
            "max_altitude_m",
            "difficulty",
            "group_size_min",
            "group_size_max",

            "best_season",
            "season_spring",
            "season_summer",
            "season_autumn",
            "season_winter",

            "price_usd",
            "discount_price_usd",

            "accommodation_summary",
            "altitude_sickness_risk",

            "cover_image",

            "is_featured",
            "is_popular",
            "is_active",
        ]

        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "category": forms.Select(
                attrs={"class": "form-select"}
            ),

            "region": forms.Select(
                attrs={"class": "form-select"}
            ),

            "guides": forms.SelectMultiple(
                attrs={
                    "class": "form-select",
                    "size": 5,
                }
            ),

            "short_description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 7,
                }
            ),

            "meta_description": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "maxlength": 160,
                }
            ),

            "duration_days": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                }
            ),

            "max_altitude_m": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                }
            ),

            "difficulty": forms.Select(
                attrs={"class": "form-select"}
            ),

            "group_size_min": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                }
            ),

            "group_size_max": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                }
            ),

            "best_season": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. Mar–May, Sep–Nov",
                }
            ),

            "season_spring": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),

            "season_summer": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),

            "season_autumn": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),

            "season_winter": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),

            "price_usd": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                    "step": "0.01",
                }
            ),

            "discount_price_usd": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                    "step": "0.01",
                }
            ),

            "accommodation_summary": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "altitude_sickness_risk": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "cover_image": forms.ClearableFileInput(
                attrs={"class": "form-control"}
            ),

            "is_featured": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),

            "is_popular": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),

            "is_active": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["guides"].queryset = (
            CustomUser.objects
            .filter(
                role=CustomUser.Role.GUIDE,
                is_active=True,
            )
            .order_by("first_name", "username")
        )


# ============================================================
# TREK CHILD FORMS
# ============================================================

class TrekItineraryDayForm(forms.ModelForm):
    class Meta:
        model = TrekItineraryDay

        fields = [
            "day_number",
            "title",
            "description",
            "altitude_m",
            "distance_km",
            "walking_hours",
            "meals",
            "accommodation",
        ]

        widgets = {
            "day_number": forms.NumberInput(
                attrs={"class": "form-control", "min": 1}
            ),

            "title": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "description": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),

            "altitude_m": forms.NumberInput(
                attrs={"class": "form-control", "min": 0}
            ),

            "distance_km": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.1"}
            ),

            "walking_hours": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.1"}
            ),

            "meals": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "accommodation": forms.TextInput(
                attrs={"class": "form-control"}
            ),
        }


class TripHighlightForm(forms.ModelForm):
    class Meta:
        model = TripHighlight

        fields = [
            "text",
            "order",
        ]

        widgets = {
            "text": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "order": forms.NumberInput(
                attrs={"class": "form-control", "min": 0}
            ),
        }


class TripInclusionForm(forms.ModelForm):
    class Meta:
        model = TripInclusion

        fields = [
            "text",
            "is_included",
            "order",
        ]

        widgets = {
            "text": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "is_included": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),

            "order": forms.NumberInput(
                attrs={"class": "form-control", "min": 0}
            ),
        }


class TripFAQForm(forms.ModelForm):
    class Meta:
        model = TripFAQ

        fields = [
            "question",
            "answer",
            "order",
        ]

        widgets = {
            "question": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "answer": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),

            "order": forms.NumberInput(
                attrs={"class": "form-control", "min": 0}
            ),
        }


class TrekImageForm(forms.ModelForm):
    class Meta:
        model = TrekImage

        fields = [
            "image",
            "caption",
            "order",
        ]

        widgets = {
            "image": forms.ClearableFileInput(
                attrs={"class": "form-control"}
            ),

            "caption": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "order": forms.NumberInput(
                attrs={"class": "form-control", "min": 0}
            ),
        }


# ============================================================
# INLINE FORMSETS
# ============================================================

TrekItineraryFormSet = inlineformset_factory(
    Trek,
    TrekItineraryDay,
    form=TrekItineraryDayForm,
    extra=1,
    can_delete=True,
)


TripHighlightFormSet = inlineformset_factory(
    Trek,
    TripHighlight,
    form=TripHighlightForm,
    extra=1,
    can_delete=True,
)


TripInclusionFormSet = inlineformset_factory(
    Trek,
    TripInclusion,
    form=TripInclusionForm,
    extra=1,
    can_delete=True,
)


TripFAQFormSet = inlineformset_factory(
    Trek,
    TripFAQ,
    form=TripFAQForm,
    extra=1,
    can_delete=True,
)


TrekImageFormSet = inlineformset_factory(
    Trek,
    TrekImage,
    form=TrekImageForm,
    extra=1,
    can_delete=True,
)