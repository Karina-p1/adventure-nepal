from django import forms

from .models import Trek, TrekRegion

DURATION_RANGES = {"1-3": (1, 3), "4-7": (4, 7), "8-14": (8, 14), "15+": (15, None)}
DURATION_CHOICES = [("", "Any length"), ("1-3", "1–3 days"), ("4-7", "4–7 days"), ("8-14", "8–14 days"), ("15+", "15+ days")]
SORT_CHOICES = [
    ("recommended", "Recommended"),
    ("price_asc", "Price: low to high"),
    ("price_desc", "Price: high to low"),
    ("duration_asc", "Duration: shortest first"),
    ("newest", "Newest"),
    ("rating", "Highest rated"),
]


class TrekFilterForm(forms.Form):
    q = forms.CharField(required=False, label="Search")
    region = forms.ChoiceField(required=False, choices=[])
    category = forms.ChoiceField(required=False, choices=[("", "Any type")] + list(Trek.Category.choices))
    difficulty = forms.ChoiceField(required=False, choices=[("", "Any level")] + list(Trek.Difficulty.choices))
    duration = forms.ChoiceField(required=False, choices=DURATION_CHOICES)
    price_min = forms.IntegerField(required=False, min_value=0, label="Min price")
    price_max = forms.IntegerField(required=False, min_value=0, label="Max price")
    sort = forms.ChoiceField(required=False, choices=SORT_CHOICES)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["region"].choices = [("", "Anywhere")] + [(r.slug, r.name) for r in TrekRegion.objects.all()]
        for name, field in self.fields.items():
            css = "form-select" if isinstance(field, forms.ChoiceField) else "form-control"
            field.widget.attrs["class"] = css

    def clean(self):
        cleaned = super().clean()
        lo, hi = cleaned.get("price_min"), cleaned.get("price_max")
        if lo is not None and hi is not None and lo > hi:
            cleaned["price_min"], cleaned["price_max"] = hi, lo
        return cleaned