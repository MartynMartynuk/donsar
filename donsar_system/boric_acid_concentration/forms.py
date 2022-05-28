from django import forms
from django.core.exceptions import ValidationError
from .models import *


class AddAlbumForm(forms.ModelForm):
    """ Форма добавления нового альбома НФХ """

    class Meta:
        model = Album
        fields = ['album_file']


class AddPointsForm(forms.Form):
    """ Форма добавления экспериментальных точек на график """

    sample_time = forms.IntegerField(label='Время взятия пробы')
    sample_conc = forms.IntegerField(label='Концентрация БК')

    def clean_sample_time(self):
        time = self.cleaned_data['sample_time']
        if time < 0:
            raise ValidationError('Некорректный ввод: время отбора пробы не может быть меньше 0!')
        return time

    def clean_sample_conc(self):
        concentration = self.cleaned_data['sample_conc']
        if concentration < 0:
            raise ValidationError('Некорректный ввод: концентрация БК не может быть меньше 0!')
        return concentration


class BorCalcForm(forms.ModelForm):
    """ Форма расчета концентрации БК """
    start_time = forms.DateTimeField(input_formats=['%d.%m.%Y %H:%M'], label='Время запуска',
                                     widget=forms.DateTimeInput(
                                         format='%d.%m.%Y %H:%M',
                                         attrs={'class': 'form-control'}))
    stop_time = forms.DateTimeField(input_formats=['%d.%m.%Y %H:%M'], label='Время останова',
                                    widget=forms.DateTimeInput(
                                        format='%d.%m.%Y %H:%M',
                                        attrs={'class': 'form-control'}))

    class Meta:
        model = CalculationResult
        fields = '__all__'

    # power_before_stop = forms.IntegerField(label='Мощность ЯР до остановки (% от Nном)')
    # effective_days_worked = forms.IntegerField(label='Число отработанных эффективных суток')
    # rod_height_before_stop = forms.IntegerField(label='Подъем стержней до останова (%)')
    # crit_conc_before_stop = forms.FloatField(label='Критическая концентрация БК до останова')
    # stop_time = forms.DateTimeField(input_formats=['%d.%m.%Y %H:%M'], label='Время останова')
    # start_time = forms.DateTimeField(input_formats=['%d.%m.%Y %H:%M'], label='Время запуска')
    # stop_conc = forms.FloatField(label='Стояночная концентрация БК')
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

    # def clean_start_time(self):
    #     time = self.cleaned_data['start_time']
    #     if time < 0:
    #         raise ValidationError('Некорректный ввод: время старта не может быть меньше 0!')
    #     return time
    #
    # def clean_stop_time(self):
    #     time = self.cleaned_data['stop_time']
    #     if time


""" Legacy """
# class BorCalcForm(forms.ModelForm):
#     """ Форма расчета концентрации БК """
#     class Meta:
#         model = BorCalculator
#         fields = '__all__'

# Теперь название добавляется автоматически по названию документа
# class AddAlbumNameForm(forms.ModelForm):
#     """ Форма добавления нового имени альбома НФХ """
#     class Meta:
#         model = Block
#         fields = '__all__'
