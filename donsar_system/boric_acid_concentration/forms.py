from django import forms
from django.core.exceptions import ValidationError
from .models import *
from donsar_system.settings import DATE_INPUT_FORMATS


class AddAlbumForm(forms.ModelForm):
    """ Форма добавления нового альбома НФХ """

    class Meta:
        model = Album
        fields = ['album_file']


class AddPointsForm(forms.Form):
    """ Форма добавления экспериментальных точек на график """

    sample_time = forms.DateTimeField(input_formats=DATE_INPUT_FORMATS, label='Время взятия пробы')
    sample_conc = forms.FloatField(label='Концентрация БК')

    # def clean_sample_time(self):
    #     time = self.cleaned_data['sample_time']
    #     if time < 0:
    #         raise ValidationError('Некорректный ввод: время отбора пробы не может быть меньше 0!')
    #     return time
    #
    def clean_sample_conc(self):
        concentration = self.cleaned_data['sample_conc']
        if concentration < 0:
            raise ValidationError('Некорректный ввод: концентрация БК не может быть меньше 0!')
        return concentration


class BorCalcForm(forms.Form):
    """ Форма расчета концентрации БК """

    power_before_stop = forms.IntegerField(label='Мощность ЯР до остановки (% от Nном)')
    effective_days_worked = forms.IntegerField(label='Число отработанных эффективных суток')
    rod_height_before_stop = forms.IntegerField(label='Подъем стержней до останова (%)')
    crit_conc_before_stop = forms.FloatField(label='Критическая концентрация БК до останова')
    stop_time = forms.DateTimeField(input_formats=DATE_INPUT_FORMATS, label='Время останова')
    start_time = forms.DateTimeField(input_formats=DATE_INPUT_FORMATS, label='Время запуска')
    stop_conc = forms.FloatField(label='Стояночная концентрация БК')
    block = forms.ModelChoiceField(queryset=Block.objects.all(), label='Блок и загрузка', empty_label='Не выбрано')

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

    def clean_stop_conc(self):
        concentration = self.cleaned_data['stop_conc']
        if concentration < 10:
            raise ValidationError('Стояночная концентрация должна превышать 10 г/дм3')
        return concentration

    # def clean_start_time(self):
    #     time = self.cleaned_data['start_time']
    #     if time < 0:
    #         raise ValidationError('Некорректный ввод: время старта не может быть меньше 0!')
    #     return time
    #
    # def clean_stop_time(self):
    #     time = self.cleaned_data['stop_time']
    #     if time

