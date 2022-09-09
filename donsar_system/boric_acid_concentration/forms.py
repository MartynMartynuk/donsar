import datetime
from collections import namedtuple
from django import forms
from django.core.exceptions import ValidationError
from django.forms import DateInput

from .models import *
from boric_acid_concentration.services.views_handler import *
from boric_acid_concentration.services.water_exchange_function import *

ReturnNamedtuple = namedtuple('ReturnNamedtuple', [
    'critical_curve',
    'setting_curve',
    'water_exchange_curve',
    'exp_water_exchange',
    'block_'
])

MINUTE_IN_MILLISECONDS = 60000


class AddAlbumForm(forms.ModelForm):
    """ Форма добавления нового альбома НФХ """

    class Meta:
        model = Album
        fields = ['album_file']


class AddPointsForm(forms.Form):
    """ Форма добавления экспериментальных точек на график """

    sample_time = forms.DateTimeField(input_formats=DATE_INPUT_FORMATS, label='Время взятия пробы',
                                      widget=DateInput(attrs={'type': 'datetime-local'}))
    sample_conc = forms.FloatField(label='Концентрация БК')

    def clean_sample_conc(self):
        concentration = self.cleaned_data['sample_conc']
        if concentration < 0:
            raise ValidationError('Некорректный ввод: концентрация БК не может быть меньше 0!')
        return concentration


class BorCalcResumeForm(forms.Form):
    """ Форма расчета концентрации БК """

    power_before_stop = forms.IntegerField(label='Мощность ЯР до остановки (% от Nном)')
    effective_days_worked = forms.IntegerField(label='Число отработанных эффективных суток')
    rod_height_before_stop = forms.IntegerField(label='Подъем стержней до останова, %')
    crit_conc_before_stop = forms.FloatField(label='Концентрация БК до останова, г/дм<sup>3</sup>')
    stop_time = forms.DateTimeField(input_formats=DATE_INPUT_FORMATS, label='Время останова',
                                    widget=DateInput(attrs={'type': 'datetime-local'}))
    water_exchange_start_time = forms.DateTimeField(input_formats=DATE_INPUT_FORMATS, label='Время начала водообмена',
                                     widget=DateInput(attrs={'type': 'datetime-local'}))
    stop_conc = forms.FloatField(label='Стояночная концентрация БК, г/дм<sup>3</sup>')
    block = forms.ModelChoiceField(queryset=Block.objects.all(), label='Блок и загрузка', empty_label='Не выбран')

    def bor_calc_handler(self) -> ReturnNamedtuple:
        block_id = self.cleaned_data['block'].pk
        block_name = self.cleaned_data['block']

        stop_reactor_time = self.cleaned_data['stop_time']
        water_exchange_start_time = self.cleaned_data['water_exchange_start_time']

        stop_time = get_epoch_time(stop_reactor_time.replace(tzinfo=None)
                                   -datetime.timedelta(hours=4))
        start_time = get_epoch_time(water_exchange_start_time.replace(tzinfo=None)
                                      - datetime.timedelta(hours=4))

        critical_curve = []
        setting_curve = []
        water_exchange_curve = []

        current_time = stop_time
        while current_time < start_time:
            critical_conc = get_critical_concentration(
                stop_time,
                current_time,
                self.cleaned_data['power_before_stop'],
                self.cleaned_data['effective_days_worked'],
                self.cleaned_data['rod_height_before_stop'],
                self.cleaned_data['crit_conc_before_stop'],
                block_id
            )
            critical_curve.append({'date': current_time,
                                   'value': critical_conc})
            setting_curve.append({'date': current_time,
                                  'value': get_setting_width(critical_curve[-1]['value'])})
            current_time += MINUTE_IN_MILLISECONDS
            print(current_time)

            # if len(critical_curve) > 1000:
            #     break

        # while current_time >=start_time:
        #     pass
        #     current_time += MINUTE_IN_MILLISECONDS




        # start_time = get_time_in_minutes(self.cleaned_data['start_time'], self.cleaned_data['stop_time'])
        # stop_conc = self.cleaned_data['stop_conc']
        #
        # maximum_time = get_maximum_time(start_time)  # время, до которого рисуем кривые концентраций
        #
        #
        # setting_curve = setting_curve_plotter(maximum_time, critical_curve)
        #
        # water_exchange_curve = water_exchange_plotter(start_time, maximum_time, self.cleaned_data['stop_conc'],
        #                                               critical_curve, setting_curve)

        # CalculationResult.objects.all().delete()  # защищает от переполнения
        #
        # CalculationResult.objects.create(critical_curve=critical_curve,
        #                                  setting_curve=setting_curve,
        #                                  water_exchange_curve=water_exchange_curve,
        #                                  start_time=start_time,
        #                                  stop_time=self.cleaned_data['stop_time'],
        #                                  stop_conc=stop_conc,
        #                                  exp_exchange_curve={},
        #                                  block=block_name)

        return ReturnNamedtuple(
            critical_curve=critical_curve,
            setting_curve=setting_curve,
            water_exchange_curve=water_exchange_curve,
            exp_water_exchange={},
            block_=block_name
        )

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

    # def clean_stop_conc(self):
    #     concentration = self.cleaned_data['stop_conc']
    #     if concentration < 10:
    #         raise ValidationError('Стояночная концентрация должна превышать 10 г/дм<sup>3</sup>')
    #     return concentration


class BorCalcStartForm(forms.Form):
    """ Форма расчета концентрации БК при первом старте после ППР """
    water_exchange_start_time = forms.DateTimeField(input_formats=DATE_INPUT_FORMATS, label='Время начала водообмена',
                                                    widget=DateInput(attrs={'type': 'datetime-local'}))
    stop_conc = forms.FloatField(label='Стояночная концентрация БК, г/дм<sup>3</sup>')
    critical_conc = forms.FloatField(label='Критическая концентрация БК, г/дм<sup>3</sup>')
    block = forms.ModelChoiceField(queryset=Block.objects.all(), label='Блок и загрузка', empty_label='Не выбран')

    def bor_calc_handler(self) -> ReturnNamedtuple:
        # считывание формы
        block_name = str(self.cleaned_data['block'])
        water_exchange_start_time = self.cleaned_data['water_exchange_start_time']
        start_conc = self.cleaned_data['stop_conc']
        critical_conc = self.cleaned_data['critical_conc']

        # константы
        rate_40 = 40
        rate_10 = 10

        setting_width = get_setting_width(critical_conc)

        current_time = get_epoch_time(water_exchange_start_time.replace(tzinfo=None)
                                      - datetime.timedelta(hours=4)) # для очевидного подгона времени
        start_time = current_time
        break_minutes_counter = 0

        critical_curve = []
        setting_curve = []
        water_exchange_curve = []

        we_conc = water_exchange_calculator(start_conc, rate_40, (current_time - start_time)/3600000)

        while we_conc > critical_conc + setting_width:
            critical_curve.append({'date': current_time, 'value': self.cleaned_data['critical_conc']})
            setting_curve.append({'date': current_time, 'value': critical_conc + setting_width})
            water_exchange_curve.append({'date': current_time, 'value': we_conc})

            current_time += MINUTE_IN_MILLISECONDS  # + 1 минута
            we_conc = water_exchange_calculator(start_conc, rate_40, (current_time - start_time) / 3600000)

        while we_conc <= (critical_conc + setting_width) and break_minutes_counter < 60:
            critical_curve.append({'date': current_time, 'value': self.cleaned_data['critical_conc']})
            setting_curve.append({'date': current_time, 'value': critical_conc + setting_width})
            water_exchange_curve.append({'date': current_time, 'value': water_exchange_curve[-1]['value']})

            break_minutes_counter += 1
            current_time += MINUTE_IN_MILLISECONDS  # + 1 минута

        start_time = water_exchange_curve[-1]['date']
        start_conc = water_exchange_curve[-1]['value']
        we_conc = water_exchange_calculator(start_conc, rate_10, (current_time - start_time) / 3600000)

        while we_conc > critical_conc:
            critical_curve.append({'date': current_time, 'value': self.cleaned_data['critical_conc']})
            setting_curve.append({'date': current_time, 'value': critical_conc + setting_width})
            water_exchange_curve.append({'date': current_time, 'value': we_conc})

            current_time += MINUTE_IN_MILLISECONDS  # + 1 минута
            we_conc = water_exchange_calculator(start_conc, rate_10, (current_time - start_time) / 3600000)

        return ReturnNamedtuple(
            critical_curve=critical_curve,
            setting_curve=setting_curve,
            water_exchange_curve=water_exchange_curve,
            exp_water_exchange={},
            block_=block_name
        )

    def clean_stop_conc(self):
        concentration = self.cleaned_data['stop_conc']
        if concentration < 10:
            raise ValidationError('Стояночная концентрация должна превышать 10 г/дм<sup>3</sup>')
        return concentration

    def clean_setting_interval(self):
        setting_interval = self.cleaned_data['setting_interval']
        if setting_interval < 1.3:
            raise ValidationError('Пусковой интервал не может быть меньше 1.3 г/дм<sup>3</sup>')
        return setting_interval


class LoginForm(forms.Form):
    username = forms.CharField(max_length=15, label='Логин')
    password = forms.CharField(widget=forms.PasswordInput, max_length=15, label='Пароль')
