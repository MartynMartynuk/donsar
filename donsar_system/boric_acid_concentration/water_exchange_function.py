import math
from boric_acid_concentration.calculate_function import *


def critical_curve_plotter(power_before_stop, effective_days_worked, rod_height_before_stop,
                           crit_conc_before_stop, stop_time, start_time, block_id, stop_conc):
    """
    Предоставление значений критической концентрации (от времени) для отрисовки кривой
    :param power_before_stop: мощность реактора до останова
    :param effective_days_worked: сколько эффективных суток отработал
    :param rod_height_before_stop: подъем стержней до останова
    :param crit_conc_before_stop: концентрация БК до останова
    :param stop_time: дата-время останова
    :param start_time: дата-время запуска
    :param stop_conc: стояночная концентрация (для расчета водообмена)
    :param block_id: номер загрузки и блока (нужен для запуска вложенной функции)
    """
    # время завершения ксенонового процесса
    # время запуска
    minutes_in_hour = 1440
    time_end = int(((start_time - stop_time).days * minutes_in_hour) + ((start_time - stop_time).seconds / 60))

    crit_curve = {}
    setting_curve = {}
    water_exchange_curve = {}

    static_reactivity = temp_effect(power_before_stop, effective_days_worked, block_id) + \
                        group_effect(rod_height_before_stop, effective_days_worked, block_id)

    bor_efficiency_ = bor_efficiency(effective_days_worked, block_id)

    maximum_time = time_end + time_end // 2 + 1  # время, до которого рисуем кривые концентраций

    for minute in range(0, maximum_time):
        """ToDo переопределить до куда отрисовывать график"""

        xe_effect_ = xe_effect(effective_days_worked, (minute / 60), block_id)
        tot_reactivity = static_reactivity + xe_effect_
        crit_curve[minute] = conc_calc(tot_reactivity, crit_conc_before_stop, bor_efficiency_)

    max_crit_conc = crit_curve[maximum_time - 1]
    if max_crit_conc < 7.0:
        setting_width = 1.3
    elif max_crit_conc > 10.4:
        setting_width = 1.8
    else:
        setting_width = 1.6

    for minute in range(0, maximum_time):
        setting_curve[minute] = crit_curve[minute] + setting_width

    for minute in range(0, maximum_time):
        if minute >= time_end:
            water_exchange_curve[minute] = water_exchange_calculator(stop_conc, 40, (minute - time_end) / 60)
            if water_exchange_curve[minute] <= setting_curve[minute]:
                start_break_time = minute
                end_break_time = start_break_time + 61
                break

    for minute in range(start_break_time+1, end_break_time):
        water_exchange_curve[minute] = water_exchange_curve[start_break_time]

    for minute in range(end_break_time+1, maximum_time):
        water_exchange_curve[minute] = water_exchange_calculator(water_exchange_curve[start_break_time],
                                                                 10, (minute - end_break_time) / 60)
        if water_exchange_curve[minute] <= crit_curve[minute]:
            break

    return crit_curve, stop_conc, time_end, setting_curve, water_exchange_curve


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
