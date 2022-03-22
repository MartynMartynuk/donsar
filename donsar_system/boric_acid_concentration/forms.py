from django import forms
from django.core.exceptions import ValidationError
from .models import BorCalculator


class BorCalcForm(forms.ModelForm):
    class Meta:
        model = BorCalculator
        fields = '__all__'

    # def clean_param(self):
    #     data = self.cleaned_data['param_1']
    #
    #     if not isinstance(data, float):
    #         raise ValidationError('Введены некорректные данные')
    #     return data
