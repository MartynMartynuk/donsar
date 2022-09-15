import json
from datetime import tzinfo

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.views.generic import *
from .forms import *
from .models import *
from boric_acid_concentration.services.album_handler import *
from boric_acid_concentration.services.views_handler import *
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
            sample_epoch_time = get_epoch_time(form.cleaned_data['sample_time'].replace(tzinfo=None)
                                               - datetime.timedelta(hours=4))
            sample_concentration = float(form.cleaned_data['sample_conc'])

            last_calculation_obj.experimental_exchange_curve.append(
                {'date': sample_epoch_time, 'value': sample_concentration}
            )
            last_calculation_obj.save()

            return graph_page(
                request,
                crit_curve = last_calculation_obj.critical_curve,
                setting_curve = last_calculation_obj.setting_curve,
                water_exchange_curve = last_calculation_obj.water_exchange_curve,
                break_start_time = last_calculation_obj.break_start_time,
                break_end_time = last_calculation_obj.break_end_time,
                crit_conc_time = last_calculation_obj.crit_conc_time,
                experimental_water_exchange = last_calculation_obj.experimental_exchange_curve,
                block_ = block_
            )
    else:
        form = AddPointsForm()
    exp_water_exchange_str = []
    # for i in last_calculation_obj.exp_exchange_curve.items():
    #     exp_water_exchange_str.append(f'{i[0]} | {i[1]}')
    # exp_water_exchange_str.sort()
    return render(request, 'bor_calculator/add_points_page.html', {'title': 'Добавление экспериментальных точек',
                                                                   'block_': block_,
                                                                   'form': form,})
                                                                   # 'exp_data': exp_water_exchange_str})


class BorCalcPage(FormView, TemplateView):
    def form_valid(self, form):
        output_calc = form.bor_calc_handler()
        return graph_page(
            self.request,
            crit_curve=output_calc.critical_curve,
            setting_curve=output_calc.setting_curve,
            water_exchange_curve=output_calc.water_exchange_curve,
            break_start_time=output_calc.break_start_time,
            break_end_time=output_calc.break_end_time,
            crit_conc_time=output_calc.crit_conc_time,
            experimental_water_exchange=output_calc.exp_water_exchange,
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
        crit_curve: list,
        setting_curve: list,
        water_exchange_curve: list,
        break_start_time: float,
        break_end_time: float,
        crit_conc_time: float,
        experimental_water_exchange: list,
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

    crit_curve_json = json.dumps(crit_curve)
    setting_curve_json = json.dumps(setting_curve)
    water_exchange_json = json.dumps(water_exchange_curve)
    exp_exchange_json = json.dumps(experimental_water_exchange)

    # print(list(crit_curve_json.values()))
    # print(setting_curve_json)

    print(exp_exchange_json)
    print(water_exchange_json)

    return render(
        request,
        'bor_calculator/graph_page.html',
        {'title': 'Добавление экспериментальных точек',
         'block_': block_,
         'crit_curve': crit_curve_json,
         'setting_curve': setting_curve_json,
         'water_exchange': water_exchange_json,
         'experimental_exchange': exp_exchange_json,
         'break_start_time': get_datetime_time(break_start_time),
         'break_end_time': get_datetime_time(break_end_time),
         'crit_conc_time': get_datetime_time(crit_conc_time),
         })


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
