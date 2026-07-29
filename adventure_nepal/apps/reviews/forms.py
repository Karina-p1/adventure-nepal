from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "title", "comment"]
        widgets = {
            "rating": forms.Select(
                choices=[(i, f"{i} ★") for i in range(5, 0, -1)],
                attrs={"class": "form-select"}
            ),
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Sum up your trek in a few words"}),
            "comment": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }