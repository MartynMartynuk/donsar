import base64
import datetime
import io
import json
import urllib.parse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.views.generic import *
import matplotlib.pyplot as plt
from .forms import *
from .models import *
from boric_acid_concentration.services.album_handler import *
from boric_acid_concentration.services.views_handler import *
from boric_acid_concentration.services.water_exchange_function import *
from donsar_system.settings import DATE_INPUT_FORMATS


def add_album_page(request):
    """
    Страница добавления альбома
    :param request:
    """
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = AddAlbumForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                file_name = str(request.FILES['album_file']).replace(' ', '_')
                batch_params = str(request.FILES['album_file'])[:-5].split(' ')
                block_num = batch_params[1]
                batch_num = batch_params[-1]
                try:
                    Block.objects.get(block_number=block_num, batch_number=batch_num)
                except:
                    Block.objects.create(block_number=block_num, batch_number=batch_num)
                block_id = Block.objects.get(block_number=block_num, batch_number=batch_num).pk
                document_obj = open_file(file_name)
                Album.objects.create(title='table1', content=handler(document_obj, 0, 2, 28, 1, 10), block_id=block_id)
                Album.objects.create(title='table2_start', content=handler(document_obj, 1, 1, 11, 1, 5),
                                     block_id=block_id)
                Album.objects.create(title='table2_100', content=handler(document_obj, 2, 1, 11, 1, 5),
                                     block_id=block_id)
                Album.objects.create(title='table2_200', content=handler(document_obj, 3, 1, 11, 1, 5),
                                     block_id=block_id)
                Album.objects.create(title='table2_300', content=handler(document_obj, 4, 1, 11, 1, 5),
                                     block_id=block_id)
                Album.objects.create(title='table2_400', content=handler(document_obj, 5, 1, 11, 1, 5),
                                     block_id=block_id)
                Album.objects.create(title='table2_500', content=handler(document_obj, 6, 1, 11, 1, 5),
                                     block_id=block_id)
                Album.objects.create(title='table2_end', content=handler(document_obj, 7, 1, 11, 1, 5),
                                     block_id=block_id)
                Album.objects.create(title='table3', content=handler(document_obj, 8, 2, 75, 1, 8), block_id=block_id)
                Album.objects.create(title='table4', content=handler(document_obj, 9, 1, 28, 1, 15), block_id=block_id)
                return redirect('bor_calc')
        else:
            form = AddAlbumForm()
        return render(request, 'bor_calculator/album_upload_page.html', {'title': 'Добавление альбома', 'form': form})
    else:
        return redirect('login')


def add_points(request):
    """
    Страница добавления экспериментальных точек на график
    :param request:
    :return:
    """
    last_calculation_obj = CalculationResult.objects.latest('id')
    block_ = last_calculation_obj.block
    if request.method == 'POST':
        form = AddPointsForm(request.POST)

        if form.is_valid():
            datetime_crit_axis = get_datetime_axis(get_int_lst(list(last_calculation_obj.critical_curve.keys())),
                                                   last_calculation_obj.stop_time)

            water_exchange_lst = get_int_lst(list(last_calculation_obj.water_exchange_curve.keys()))
            water_exchange_curve = dict(
                zip(water_exchange_lst, list(last_calculation_obj.water_exchange_curve.values())))
            # из-за того что в базе словарь сохраняется как json, требуется этот велосипед с пересборкой словаря
            # без него не работает ограничение вывода по оси y

            datetime_water_exchange_axis = get_datetime_axis(
                get_int_lst(list(last_calculation_obj.water_exchange_curve.keys())),
                last_calculation_obj.stop_time)

            last_calculation_obj.exp_exchange_curve[datetime.datetime.strftime(form.cleaned_data['sample_time'],
                                                                               DATE_INPUT_FORMATS[0])] \
                = float(form.cleaned_data['sample_conc'])
            last_calculation_obj.save()

            return graph_page(request,
                              last_calculation_obj.critical_curve,
                              last_calculation_obj.setting_curve,
                              water_exchange_curve,
                              last_calculation_obj.start_time,
                              last_calculation_obj.stop_conc,
                              datetime_crit_axis,
                              datetime_water_exchange_axis,
                              last_calculation_obj.exp_exchange_curve,
                              block_)
    else:
        form = AddPointsForm()
    exp_water_exchange_str = []
    for i in last_calculation_obj.exp_exchange_curve.items():
        exp_water_exchange_str.append(f'{i[0]} | {i[1]}')
    exp_water_exchange_str.sort()
    return render(request, 'bor_calculator/add_points_page.html', {'title': 'Добавление экспериментальных точек',
                                                                   'block_': block_,
                                                                   'form': form,
                                                                   'exp_data': exp_water_exchange_str})


class BorCalcPage(FormView, TemplateView):
    def form_valid(self, form):
        output_calc = form.bor_calc_handler()
        return graph_page(
            self.request,
            crit_curve_dict=output_calc.crit_curve_dict,
            setting_dict=output_calc.setting_dict,
            water_exchange_dict=output_calc.water_exchange_dict,
            start_time=output_calc.start_time,
            water_exchange_start_time=output_calc.water_exchange_start_time,
            stop_conc=output_calc.stop_conc,
            crit_axis=output_calc.crit_axis,
            water_exchange_axis=output_calc.water_exchange_axis,
            exp_water_exchange=output_calc.exp_water_exchange,
            block_=output_calc.block_
        )


class BorCalcResumePage(BorCalcPage):
    form_class = BorCalcResumeForm
    template_name = 'bor_calculator/bor_calc_page.html'


class BorCalcStartPage(BorCalcPage):
    form_class = BorCalcStartForm
    template_name = 'bor_calculator/bor_calc_page.html'


def graph_page(
        request,
        crit_curve_dict: dict,
        setting_dict,
        water_exchange_dict,
        water_exchange_start_time: datetime,
        exp_water_exchange,
        block_
):
    """
    Страница вывода графика и добавления точек экспериментальной кривой водообмена
    :param request:
    :param crit_curve_dict: словарь критических концентраций (время: значение)
    :param setting_dict: словарь уставочных концентраций (время: значение)
    :param water_exchange_dict: словарь концентраций водообмена (время: значение)
    :param stop_conc: стояночная концентрация БК
    :param start_time: время начала водообмена
    :param crit_axis: ось абсцисс формата datatime (длинная)
    :param water_exchange_axis: ось абсцисс формата datatime (короткая)
    :param exp_water_exchange: словарь экспериментальных точек
    :param block_: название блока и загрузки для вывода на верху страницы
    :return:
    """
    crit_curve_lst = list(crit_curve_dict.values())
    setting_curve_lst = list(setting_dict.values())
    water_exchange_lst = list(water_exchange_dict.values())



    def get_epoch_time(process_start_time: datetime, curve_lst: list) -> list:
        epoch = datetime.datetime.utcfromtimestamp(0)
        process_start_time_millisec = (process_start_time.replace(tzinfo=None) - epoch - datetime.timedelta(hours=9)).total_seconds() * 1000.0
        for element in curve_lst:
            element['date'] = element['date'] * 60000.0 + process_start_time_millisec
        return curve_lst

    get_epoch_time(water_exchange_start_time, crit_curve_lst)
    get_epoch_time(water_exchange_start_time, setting_curve_lst)
    get_epoch_time(water_exchange_start_time, water_exchange_lst)

    crit_curve_json = json.dumps(crit_curve_lst)
    setting_curve_json = json.dumps(setting_curve_lst)
    water_exchange_json = json.dumps(water_exchange_lst)

    # print(list(crit_curve_json.values()))
    # print(setting_curve_json)
    # print(water_exchange_json)

    return render(request,
                  'bor_calculator/graph_page.html',
                  {'title': 'Добавление экспериментальных точек',
                   'block_': block_,
                   'crit_curve_dict': crit_curve_json,
                   'setting_curve_dict': setting_curve_json,
                   'water_exchange_dict': water_exchange_json})


class LoginPage(LoginView):
    form_class = LoginForm
    template_name = 'bor_calculator/bor_calc_page.html'

    def get(self, request):
        if request.user.is_authenticated:
            user_name = request.user
            return render(request, 'logout_page.html', {'title': 'Авторизация пройдена', 'user_name': user_name})
        else:
            form = self.form_class()
            return render(request, 'login_page.html', {'title': 'Авторизация пользователя', 'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                if user.is_active:
                    login(request, user)
                    user_name = request.user
                    return render(request, 'logout_page.html', {'title': 'Авторизация пройдена',
                                                                'user_name': user_name})
                else:
                    disabled_account = 'Ваш аккаунт отключен'
                    return render(request, 'login_page.html', {'title': 'Авторизация не пройдена',
                                                               'failed_login': disabled_account,
                                                               'form': form})
            else:
                invalid_login = 'Неверное имя пользователя или пароль'
                return render(request, 'login_page.html', {'title': 'Авторизация не пройдена',
                                                           'failed_login': invalid_login,
                                                           'form': form})


def logout_user(request):
    logout(request)
    return redirect('login')
