from django import forms
from django.core.exceptions import ValidationError
from .models import BorCalculator, Album


class BorCalcForm(forms.ModelForm):
    class Meta:
        model = BorCalculator
        fields = '__all__'

    def clean_power_before_stop(self):
        power = self.cleaned_data['power_before_stop']
        valid_power_list = [104, 100, 90, 80, 70, 60, 50, 40, 30]
        if power not in valid_power_list:
            raise ValidationError('Некорректный ввод: начальная мощность должна быть одним из списка:'
                                  '[104, 100, 90, 80, 70, 60, 50, 40, 30]')
        return power

    def clean_effective_days_worked(self):
        days = self.cleaned_data['effective_days_worked']
        if days < 0 or days >= 500:
            raise ValidationError('Некорректный ввод: количество отработанных эффективных суток должно'
                                  ' лежать в диапазоне [0, 500) дней:')
        return days

    def clean_rod_height_before_stop(self):
        rod_height = self.cleaned_data['rod_height_before_stop']
        if rod_height < 0 or rod_height > 100:
            raise ValidationError('Некорректный ввод: положение 10-й группы должно быть от'
                                  '0% до 100%')
        return rod_height

    def clean_crit_conc_before_stop(self):
        concentration = self.cleaned_data['crit_conc_before_stop']
        if concentration < 0:
            raise ValidationError('Некорректный ввод: концентрация БК не может быть меньше 0!')
        return concentration

    def clean_start_time(self):
        time = self.cleaned_data['start_time']
        if time < 0:
            raise ValidationError('Некорректный ввод: время старта не может быть меньше 0!')
        return time


class UploadAlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ['album_file']
