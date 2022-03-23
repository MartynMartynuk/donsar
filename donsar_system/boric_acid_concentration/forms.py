from django import forms
from django.core.exceptions import ValidationError
from .models import BorCalculator


# class BorCalcForm(forms.ModelForm):
#     class Meta:
#         model = BorCalculator
#         fields = '__all__'


class UploadAlbumForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField()
