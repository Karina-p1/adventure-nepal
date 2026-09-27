from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CustomerProfile, CustomUser, GuideProfile


class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)

    class Meta:
        model = CustomUser
        fields = ["username", "first_name", "last_name", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = CustomUser.Role.CUSTOMER
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "email", "phone", "avatar"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "avatar": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if CustomUser.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Another account already uses this email.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        if "email" in self.changed_data:
            user.is_email_verified = False  # re-verify on email change
        if commit:
            user.save()
        return user


class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = CustomerProfile
        fields = ["address", "country", "date_of_birth", "emergency_contact_name", "emergency_contact_phone"]
        widgets = {
            "address": forms.TextInput(attrs={"class": "form-control"}),
            "country": forms.TextInput(attrs={"class": "form-control"}),
            "date_of_birth": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "emergency_contact_name": forms.TextInput(attrs={"class": "form-control"}),
            "emergency_contact_phone": forms.TextInput(attrs={"class": "form-control"}),
        }


class GuideSelfEditForm(forms.ModelForm):
    """Fields a guide may edit about themselves. Certifications and visibility stay admin-only (trust claims)."""
    class Meta:
        model = GuideProfile
        fields = ["position", "photo", "bio", "experience_years", "languages", "specialization",
                  "facebook_url", "instagram_url", "linkedin_url"]
        widgets = {
            "position": forms.TextInput(attrs={"class": "form-control"}),
            "photo": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "bio": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "experience_years": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "languages": forms.TextInput(attrs={"class": "form-control"}),
            "specialization": forms.TextInput(attrs={"class": "form-control"}),
            "facebook_url": forms.URLInput(attrs={"class": "form-control"}),
            "instagram_url": forms.URLInput(attrs={"class": "form-control"}),
            "linkedin_url": forms.URLInput(attrs={"class": "form-control"}),
        }