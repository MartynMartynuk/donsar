import math
from boric_acid_concentration.calculate_function import *


def critical_curve_plotter(power_before_stop, effective_days_worked, rod_height_before_stop,
                           crit_conc_before_stop, maximum_time, block_id):
    """
    Предоставление значений критической концентрации (от времени) для отрисовки кривой
    :param power_before_stop: мощность реактора до останова
    :param effective_days_worked: сколько эффективных суток отработал
    :param rod_height_before_stop: подъем стержней до останова
    :param crit_conc_before_stop: концентрация БК до останова
    :param block_id: номер загрузки и блока (нужен для запуска вложенной функции)
    :param maximum_time: время, до которого рисуем кривые концентраций
    :return: словарь критических концентраций
    """
    crit_curve = {}

    static_reactivity = temp_effect(power_before_stop, effective_days_worked, block_id) + \
                        group_effect(rod_height_before_stop, effective_days_worked, block_id)

    bor_efficiency_ = bor_efficiency(effective_days_worked, block_id)

    xenon_table = Album.objects.get(title='table3', block_id=block_id).content

    for minute in range(0, maximum_time):
        xe_effect_ = xe_effect(effective_days_worked, (minute / 60), xenon_table)
        tot_reactivity = static_reactivity + xe_effect_
        crit_curve[minute] = conc_calc(tot_reactivity, crit_conc_before_stop, bor_efficiency_)
    return crit_curve


def setting_curve_plotter(maximum_time, crit_curve: dict):
    """
    Предоставление значений "уставочной" концентрации (от времени) для отрисовки кривой
    :param maximum_time: время, до которого рисуем кривые концентраций
    :param crit_curve: словарь критических концентраций
    :return: словарь "уставочных" концентраций
    """
    max_crit_conc = crit_curve[maximum_time - 1]
    if max_crit_conc < 7.0:
        setting_width = 1.3
    elif max_crit_conc > 10.4:
        setting_width = 1.8
    else:
        setting_width = 1.6

    setting_curve = {}
    for minute in range(0, maximum_time):
        setting_curve[minute] = crit_curve[minute] + setting_width
    return setting_curve


def water_exchange_plotter(start_time, maximum_time, stop_conc, crit_curve: dict, setting_curve: dict):
    """
    Предоставление значений концентраций водообмена (от времени) для отрисовки кривой
    :param start_time: время начала водообмена
    :param maximum_time: время, до которого рисуем кривые концентраций
    :param stop_conc: стояночная концентрация
    :param crit_curve: словарь критических концентраций
    :param setting_curve: словарь "уставочных" концентраций
    :return: словарь концентраций водообмена
    """
    water_exchange_curve = {}
    for minute in range(start_time, maximum_time):
        water_exchange_curve[minute] = water_exchange_calculator(stop_conc, 40, (minute - start_time) / 60)
        if water_exchange_curve[minute] <= setting_curve[minute]:
            start_break_time = minute
            end_break_time = start_break_time + 61
            break

    for minute in range(start_break_time + 1, end_break_time):
        water_exchange_curve[minute] = water_exchange_curve[start_break_time]

    for minute in range(end_break_time + 1, maximum_time):
        water_exchange_curve[minute] = water_exchange_calculator(water_exchange_curve[start_break_time],
                                                                 10, (minute - end_break_time) / 60)
        if water_exchange_curve[minute] <= crit_curve[minute]:
            break
    return water_exchange_curve


def water_exchange_calculator(c_start, rate, time, po_pr=0.992, po=0.767, v=338):
    """
    Расчет теоретической кривой водообмена
    :param c_start: стартовая (стояночная) концентрация [г/дм3]
    :param rate: расход [т/ч]
    :param time: время водообмена [ч]
    :param po_pr: плотность продувки
    :param po: плотность раствора
    :param v: объем 1 контура
    :return: концентрация [г/дм3]
    """
    return c_start * math.exp(-(rate * po_pr) / (po * v) * time)
