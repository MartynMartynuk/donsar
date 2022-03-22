from django import forms
from django.core.exceptions import ValidationError


class BorCalcForm(forms.Form):
    param_1 = forms.FloatField(help_text='Введите параметр 1')

    def clean_param(self):
        data = self.cleaned_data['param_1']

        if not isinstance(data, float):
            raise ValidationError('Введены некорректные данные')
        return data
