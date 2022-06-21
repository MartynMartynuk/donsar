import base64
import io
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
        return graph_page(self.request,
                          crit_curve_dict=output_calc['crit_curve_dict'],
                          setting_dict=output_calc['setting_dict'],
                          water_exchange_dict=output_calc['water_exchange_dict'],
                          start_time=output_calc['start_time'],
                          stop_conc=output_calc['stop_conc'],
                          crit_axis=output_calc['crit_axis'],
                          water_exchange_axis=output_calc['water_exchange_axis'],
                          exp_water_exchange=output_calc['exp_water_exchange'],
                          block_=output_calc['block_'])


class BorCalcResumePage(BorCalcPage):
    form_class = BorCalcResumeForm
    template_name = 'bor_calculator/bor_calc_page.html'


class BorCalcStartPage(BorCalcPage):
    form_class = BorCalcStartForm
    template_name = 'bor_calculator/bor_calc_page.html'


def graph_page(request, crit_curve_dict, setting_dict, water_exchange_dict, start_time, stop_conc, crit_axis,
               water_exchange_axis, exp_water_exchange, block_):
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
    # ToDo выглядит как велосипед, переделать бы отсюда
    if (water_exchange_axis[-1] - water_exchange_axis[0]) < datetime.timedelta(hours=10):
        x_current = water_exchange_axis[0] - datetime.timedelta(minutes=water_exchange_axis[0].minute) \
            if water_exchange_axis[0].minute != 0 \
            else water_exchange_axis[0] - datetime.timedelta(hours=1)
        x_end_point = water_exchange_axis[-1] + datetime.timedelta(hours=1)
        crit_axis_str = []
        while x_current <= x_end_point:
            crit_axis_str.append(datetime.datetime.strftime(x_current, DATE_INPUT_FORMATS[0]))
            x_current += datetime.timedelta(hours=1)
    else:
        if water_exchange_axis[0].hour % 2 == 0:
            x_current = water_exchange_axis[0] - datetime.timedelta(minutes=water_exchange_axis[0].minute)
        elif water_exchange_axis[0].minute != 0:
            x_current = water_exchange_axis[0] - datetime.timedelta(minutes=water_exchange_axis[0].minute - 60)
        else:
            x_current = water_exchange_axis[0] - datetime.timedelta(hours=1)
        x_end_point = water_exchange_axis[-1] + datetime.timedelta(hours=2)
        crit_axis_str = []
        while x_current <= x_end_point:
            crit_axis_str.append(datetime.datetime.strftime(x_current, DATE_INPUT_FORMATS[0]))
            x_current += datetime.timedelta(hours=2)
    # ToDo переделать до сюда

    fig, ax = plt.subplots()
    plt.plot(crit_axis,
             list(crit_curve_dict.values()),
             color='r',
             label='Критическая концентрация БК',
             linewidth=1)
    plt.plot(crit_axis,
             list(setting_dict.values()),
             color='b',
             label='Начало пускового диапазона',
             linewidth=1)
    plt.plot(water_exchange_axis,
             list(water_exchange_dict.values()),
             color='g',
             label='Концентрация БК при водообмене',
             linewidth=1)
    plt.plot(datetime_dict_to_lst(exp_water_exchange)[0],
             datetime_dict_to_lst(exp_water_exchange)[1],
             color='cyan',
             marker='x',
             label='Практические значения концентрации БК',
             linewidth=1)

    crit_time = datetime.datetime.strftime(water_exchange_axis[-1], DATE_INPUT_FORMATS[0])

    plt.xlabel('Время')
    plt.ylabel(r'Концентрация БК, г/$дм^{3}$')
    plt.minorticks_on()
    plt.grid(which='major', linewidth=0.5)
    plt.grid(which='minor', linestyle=':')
    plt.legend(loc='upper right', shadow=False, fontsize=9)

    ax.set_xticklabels(crit_axis_str)
    plt.tick_params(axis='x', labelrotation=90)

    water_exchange_end_time = len(water_exchange_dict) + start_time
    plt.xlim(water_exchange_axis[0] - datetime.timedelta(hours=1),
             water_exchange_axis[-1] + datetime.timedelta(hours=1))
    plt.ylim((water_exchange_dict[int(water_exchange_end_time) - 1] - 0.5, stop_conc + 0.1))

    fig = plt.gcf()
    plt.savefig('graphs/График.png')
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)

    exp_water_exchange_str = []
    for i in exp_water_exchange.items():
        exp_water_exchange_str.append(f'{i[0]} | {i[1]}')
    exp_water_exchange_str.sort()

    return render(request,
                  'bor_calculator/graph_page.html',
                  {'title': 'Добавление экспериментальных точек',
                   'block_': block_, 'graph': uri,
                   'crit_time': crit_time,
                   'exp_data': exp_water_exchange_str})


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
