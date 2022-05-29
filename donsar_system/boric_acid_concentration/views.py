import base64
import datetime
import io
import time
import urllib.parse
from django.shortcuts import render, redirect
import matplotlib.pyplot as plt
from .forms import *
from .models import *
from .album_handler import *
from .views_handler import get_start_time, get_maximum_time, get_datetime_axis, get_int_lst, datetime_dict_to_lst
from .water_exchange_function import *


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
    if request.method == 'POST':
        form = AddPointsForm(request.POST)

        if form.is_valid():
            last_calculation_obj = CalculationResult.objects.latest('id')

            datetime_crit_axis = get_datetime_axis(get_int_lst(list(last_calculation_obj.critical_curve.keys())),
                                                   last_calculation_obj.stop_time)
            datetime_water_exchange_axis = get_datetime_axis(get_int_lst(list(last_calculation_obj.water_exchange_curve.keys())),
                                                             last_calculation_obj.stop_time)

            last_calculation_obj.exp_exchange_curve[datetime.datetime.strftime(form.cleaned_data['sample_time'], '%d.%m.%Y %H:%M')] \
                = form.cleaned_data['sample_conc']
            last_calculation_obj.save()
            # print(last_calculation_obj.exp_exchange_curve)

            return graph_page(request,
                              last_calculation_obj.critical_curve,
                              last_calculation_obj.setting_curve,
                              last_calculation_obj.water_exchange_curve,
                              last_calculation_obj.start_time,
                              last_calculation_obj.stop_conc,
                              datetime_crit_axis,
                              datetime_water_exchange_axis,
                              last_calculation_obj.exp_exchange_curve)
    else:
        form = AddPointsForm()
    return render(request, 'bor_calculator/add_points_page.html', {'title': 'Добавление экспериментальных точек',
                                                                   'form': form})


def bor_calc_page(request):
    """
    Страница формы
    :param request:
    :return:
    """
    if request.method == 'POST':
        form = BorCalcForm(request.POST)
        if form.is_valid():
            block_id = int(request.POST['block'])

            start_time = get_start_time(form.cleaned_data['start_time'], form.cleaned_data['stop_time'])
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
            # for i in list(critical_curve.keys()):
            #     datetime_crit_axis.append(form.cleaned_data['stop_time'] + datetime.timedelta(minutes=i))
            # for i in list(water_exchange_curve.keys()):
            #     datetime_water_exchange_axis.append(form.cleaned_data['stop_time'] + datetime.timedelta(minutes=i))

            CalculationResult.objects.create(critical_curve=critical_curve,
                                             setting_curve=setting_curve,
                                             water_exchange_curve=water_exchange_curve,
                                             start_time=start_time,
                                             stop_time=form.cleaned_data['stop_time'],
                                             stop_conc=stop_conc,
                                             exp_exchange_curve={})

            return graph_page(request, critical_curve, setting_curve, water_exchange_curve, start_time, stop_conc,
                              datetime_crit_axis, datetime_water_exchange_axis, {})
    else:
        form = BorCalcForm()
    return render(request, 'bor_calculator/bor_calc_page.html', {'title': 'Расчет концентрации БК', 'form': form})


def graph_page(request, crit_curve_dict, setting_dict, water_exchange_dict, start_time, stop_conc, crit_axis,
               water_exchange_axis, exp_water_exchange):
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
    :return:
    """
    crit_axis_str = ['25.04.22\n10:00', '25.04.22 11:00', '25.04.22 12:00', '25.04.22 13:00',
                     '25.04.22 14:00', '25.04.22 15:00', '25.04.22 16:00', '25.04.22 17:00']
    # water_exchange_axis_str = []
    # for i in crit_axis:
    #     crit_axis_str.append(datetime.datetime.strftime(i, '%d.%m.%Y %H:%M'))
    # for i in water_exchange_axis:
    #     water_exchange_axis_str.append(datetime.datetime.strftime(i, '%d.%m.%Y %H:%M'))
    # print(crit_axis_str, water_exchange_axis_str)
    # print('!!!!')

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

    plt.xlabel('Время, мин')
    plt.ylabel(r'Концентрация БК, г/$дм^{3}$')
    plt.minorticks_on()
    plt.grid(which='major', linewidth=0.5)
    plt.grid(which='minor', linestyle=':')
    plt.legend(loc='upper right', shadow=False, fontsize=9)

    # ax.set_xticklabels(crit_axis_str)
    # plt.tick_params(axis='x', labelrotation=90)

    water_exchange_end_time = len(water_exchange_dict) + start_time
    plt.xlim(water_exchange_axis[0]-datetime.timedelta(hours=1),
             water_exchange_axis[-1]+datetime.timedelta(hours=1))
    plt.ylim((water_exchange_dict[str(int(water_exchange_end_time) - 1)] - 0.5, stop_conc + 0.1))

    fig = plt.gcf()
    plt.savefig('graphs/График.png')
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)

    return render(request, 'bor_calculator/graph_page.html', {'title': 'Добавление экспериментальных точек',
                                                              'graph': uri})
