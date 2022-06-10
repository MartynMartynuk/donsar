import base64
import io
import urllib.parse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
import matplotlib.pyplot as plt
from .forms import *
from .models import *
from .album_handler import *
from .views_handler import *
from .water_exchange_function import *
from donsar_system.settings import DATE_INPUT_FORMATS


@login_required(login_url='/login/')
def add_album_page(request):
    """
    Страница добавления альбома
    :param request:
    """
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
            Album.objects.create(title='table2_start', content=handler(document_obj, 1, 1, 11, 1, 5), block_id=block_id)
            Album.objects.create(title='table2_100', content=handler(document_obj, 2, 1, 11, 1, 5), block_id=block_id)
            Album.objects.create(title='table2_200', content=handler(document_obj, 3, 1, 11, 1, 5), block_id=block_id)
            Album.objects.create(title='table2_300', content=handler(document_obj, 4, 1, 11, 1, 5), block_id=block_id)
            Album.objects.create(title='table2_400', content=handler(document_obj, 5, 1, 11, 1, 5), block_id=block_id)
            Album.objects.create(title='table2_500', content=handler(document_obj, 6, 1, 11, 1, 5), block_id=block_id)
            Album.objects.create(title='table2_end', content=handler(document_obj, 7, 1, 11, 1, 5), block_id=block_id)
            Album.objects.create(title='table3', content=handler(document_obj, 8, 2, 75, 1, 8), block_id=block_id)
            Album.objects.create(title='table4', content=handler(document_obj, 9, 1, 28, 1, 15), block_id=block_id)
            return redirect('bor_calc')
    else:
        form = AddAlbumForm()
    return render(request, 'bor_calculator/album_upload_page.html', {'title': 'Добавление альбома', 'form': form})


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
    return render(request, 'bor_calculator/add_points_page.html', {'title': 'Добавление экспериментальных точек',
                                                                   'block_': block_,
                                                                   'form': form,
                                                                   'exp_data': exp_water_exchange_str})


def bor_calc_start_page(request):
    """
    Страница заполнения данных для расчета при первом запуске после ППР
    :param request:
    :return:
    """
    if request.method == 'POST':
        form = BorCalcStartForm(request.POST)
        if form.is_valid():
            block_name = str(Block.objects.get(pk=int(request.POST['block'])))
            water_exchange_start_time = form.cleaned_data['water_exchange_start_time']

            time_before_start = 5  # для начала оси координат до старта водообмена
            time_after_start = 20  # костыль для рисования оси координат вперед
            crit_axis_start_time = water_exchange_start_time - datetime.timedelta(hours=time_before_start)
            crit_axis_end_time = water_exchange_start_time + datetime.timedelta(hours=time_after_start)
            start_time = time_before_start * 60  # время начала водообмена в минутах
            minutes = get_time_in_minutes(crit_axis_end_time, crit_axis_start_time)

            critical_curve = get_static_concentration(0, minutes, form.cleaned_data['critical_conc'])
            setting_curve = get_setting_curve(critical_curve, form.cleaned_data['setting_interval'])

            water_exchange_curve = water_exchange_plotter(start_time,
                                                          minutes,
                                                          form.cleaned_data['stop_conc'],
                                                          critical_curve,
                                                          setting_curve)

            datetime_crit_axis = get_datetime_axis(list(critical_curve.keys()),
                                                   crit_axis_start_time)
            datetime_water_exchange_axis = get_datetime_axis(list(water_exchange_curve.keys()),
                                                             crit_axis_start_time)

            CalculationResult.objects.create(critical_curve=critical_curve,
                                             setting_curve=setting_curve,
                                             water_exchange_curve=water_exchange_curve,
                                             start_time=start_time,
                                             stop_time=crit_axis_start_time,
                                             stop_conc=form.cleaned_data['stop_conc'],
                                             exp_exchange_curve={},
                                             block=block_name)

            return graph_page(request,
                              crit_curve_dict=critical_curve,
                              setting_dict=setting_curve,
                              water_exchange_dict=water_exchange_curve,
                              start_time=start_time,
                              stop_conc=form.cleaned_data['stop_conc'],
                              crit_axis = datetime_crit_axis,
                              water_exchange_axis = datetime_water_exchange_axis,
                              exp_water_exchange={},
                              block_=block_name)
    else:
        form = BorCalcStartForm()
    return render(request, 'bor_calculator/bor_calc_start_page.html', {'title': 'Расчет концентрации БК',
                                                                       'form': form})


def bor_calc_resume_page(request):
    """
    Страница заполнения данных для расчета при повторном запуске
    :param request:
    :return:
    """
    if request.method == 'POST':
        form = BorCalcResumeForm(request.POST)
        if form.is_valid():
            block_id = int(request.POST['block'])
            block_name = str(Block.objects.get(pk=block_id))

            start_time = get_time_in_minutes(form.cleaned_data['start_time'], form.cleaned_data['stop_time'])
            stop_conc = form.cleaned_data['stop_conc']

            maximum_time = get_maximum_time(start_time)  # время, до которого рисуем кривые концентраций

            critical_curve = critical_curve_plotter(form.cleaned_data['power_before_stop'],
                                                    form.cleaned_data['effective_days_worked'],
                                                    form.cleaned_data['rod_height_before_stop'],
                                                    form.cleaned_data['crit_conc_before_stop'],
                                                    maximum_time,
                                                    block_id)

            setting_curve = setting_curve_plotter(maximum_time, critical_curve)

            water_exchange_curve = water_exchange_plotter(start_time, maximum_time, form.cleaned_data['stop_conc'],
                                                          critical_curve, setting_curve)

            datetime_crit_axis = get_datetime_axis(list(critical_curve.keys()),
                                                   form.cleaned_data['stop_time'])
            datetime_water_exchange_axis = get_datetime_axis(list(water_exchange_curve.keys()),
                                                             form.cleaned_data['stop_time'])

            CalculationResult.objects.create(critical_curve=critical_curve,
                                             setting_curve=setting_curve,
                                             water_exchange_curve=water_exchange_curve,
                                             start_time=start_time,
                                             stop_time=form.cleaned_data['stop_time'],
                                             stop_conc=stop_conc,
                                             exp_exchange_curve={},
                                             block=block_name)

            return graph_page(request,
                              critical_curve,
                              setting_curve,
                              water_exchange_curve,
                              start_time,
                              stop_conc,
                              datetime_crit_axis,
                              datetime_water_exchange_axis,
                              {},
                              block_name)
    else:
        form = BorCalcResumeForm()
    return render(request, 'bor_calculator/bor_calc_resume_page.html', {'title': 'Расчет концентрации БК',
                                                                        'form': form})


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
    :return:
    """
    x_current = water_exchange_axis[0] - datetime.timedelta(minutes=water_exchange_axis[0].minute) \
        if water_exchange_axis[0].minute != 0 \
        else water_exchange_axis[0] - datetime.timedelta(hours=1)
    x_end_point = water_exchange_axis[-1] + datetime.timedelta(hours=1)
    crit_axis_str = []
    while x_current <= x_end_point:
        crit_axis_str.append(datetime.datetime.strftime(x_current, DATE_INPUT_FORMATS[0]))
        x_current += datetime.timedelta(hours=1)

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

    ax.set_xticklabels(crit_axis_str)  # ToDo работает не всегда, надо пересмотреть
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

    return render(request, 'bor_calculator/graph_page.html', {'title': 'Добавление экспериментальных точек',
                                                              'block_': block_, 'graph': uri,
                                                              'crit_time': crit_time,
                                                              'exp_data': exp_water_exchange_str})


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'],
                                password=form.cleaned_data['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('bor_calc')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


def user_logout(request):
    logout(request)
    return render(request, 'logout.html')
