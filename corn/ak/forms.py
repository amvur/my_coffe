from django import forms
from .models import Ak


class AkForms(forms.ModelForm):
    class Meta:
        model = Ak
        fields = ['view', 'name_firma', 'inn', 'kPP', 'Address', 'email', 'director']