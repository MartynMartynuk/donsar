from django import forms
from django.core.exceptions import ValidationError
from .models import BorCalculator, Album


class BorCalcForm(forms.ModelForm):
    class Meta:
        model = BorCalculator
        fields = '__all__'


class UploadAlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = '__all__'
