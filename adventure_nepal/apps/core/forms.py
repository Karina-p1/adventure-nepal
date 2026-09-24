from django import forms


class NewsletterForm(forms.Form):
    email = forms.EmailField(max_length=254)
    website = forms.CharField(required=False)  # honeypot: real users never fill this in

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()