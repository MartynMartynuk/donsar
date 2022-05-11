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
    time_end = int(((start_time - stop_time).days * 1440) + ((start_time - stop_time).seconds / 60))

    crit_curve = {}
    setting_curve = {}
    water_exchange_curve = {}

    static_reactivity = temp_effect(power_before_stop, effective_days_worked, block_id) + \
                        group_effect(rod_height_before_stop, effective_days_worked, block_id)

    bor_efficiency_ = bor_efficiency(effective_days_worked, block_id)

    max_crit_conc = 10

    if max_crit_conc < 7.0:
        setting_width = 1.3
    elif max_crit_conc > 10.4:
        setting_width = 1.8
    else:
        setting_width = 1.6

    for current_time in range(0, time_end+time_end//2):  # костыль, чтобы взять пошире на графике
        """ToDo переопределить до куда отрисовывать график"""

        xe_effect_ = xe_effect(effective_days_worked, (current_time/60), block_id)
        crit_curve[current_time] = crit_conc_before_stop + (static_reactivity + xe_effect_)/(-bor_efficiency_)

        setting_curve[current_time] = crit_curve[current_time] + setting_width

    for current_time in range(0, time_end+time_end//2):
        if current_time >= time_end:
            water_exchange_curve[current_time] = water_exchange_calculator(stop_conc, 40, current_time - time_end)
            if water_exchange_curve[current_time] <= setting_curve[current_time]:
                break_time = current_time
                water_exchange_curve[current_time + 1] = water_exchange_curve[current_time]
                break

    for current_time in range(break_time + 2, time_end+time_end//2):
        water_exchange_curve[current_time] = water_exchange_calculator(water_exchange_curve[break_time + 1], 10,
                                                                       current_time - time_end)
        if water_exchange_curve[current_time] <= crit_curve[current_time]:
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
