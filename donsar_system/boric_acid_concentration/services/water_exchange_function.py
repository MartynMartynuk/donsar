import math
from boric_acid_concentration.services.calculate_function import *


def get_critical_concentration(
        stop_time: float,
        current_time: float,
        power_before_stop: float,
        effective_days_worked: float,
        rod_height_before_stop: float,
        crit_conc_before_stop: float,
        block_id: object
) -> float:
    """
    Предоставление значений критической концентрации (от времени) для отрисовки кривой
    :param stop_time:
    :param current_time:
    :return:
    :param power_before_stop: мощность реактора до останова
    :param effective_days_worked: сколько эффективных суток отработал
    :param rod_height_before_stop: подъем стержней до останова
    :param crit_conc_before_stop: концентрация БК до останова
    :param block_id: номер загрузки и блока (нужен для запуска вложенной функции)
    :param maximum_time: время, до которого рисуем кривые концентраций
    :return: словарь критических концентраций
    """
    static_reactivity = temp_effect(power_before_stop, effective_days_worked, block_id) + \
                        group_effect(rod_height_before_stop, effective_days_worked, block_id)

    bor_efficiency_ = bor_efficiency(effective_days_worked, block_id)

    xenon_table = Album.objects.get(title='table3', block_id=block_id).content
    xe_effect_ = xe_effect(effective_days_worked, (current_time - stop_time)/3600000, xenon_table)  # ToDo возможна ошибка
    tot_reactivity = static_reactivity + xe_effect_
    return conc_calc(tot_reactivity, crit_conc_before_stop, bor_efficiency_)


# ToDo Объединить! Dry!
def setting_curve_plotter(maximum_time, crit_curve: dict):
    """
    Предоставление значений "уставочной" концентрации (от времени) для отрисовки кривой
    :param maximum_time: время, до которого рисуем кривые концентраций
    :param crit_curve: словарь критических концентраций
    :return: словарь "уставочных" концентраций
    """
    max_crit_conc = crit_curve[maximum_time - 1]
    setting_width = get_setting_width(max_crit_conc)

    setting_curve = {}
    graph_counter = 0
    for minute in range(0, maximum_time):
        setting_curve[graph_counter] = {'date': minute,
                                        'value': crit_curve[minute] + setting_width}
        graph_counter += 1
    return setting_curve


def get_setting_width(critical_conc):
    """
    Выбирает ширину пускового диапазона
    :param critical_conc: критическая концентрация БК
    :return:
    """
    if critical_conc < 7.0:
        return 1.3
    elif critical_conc > 10.4:
        return 1.8
    else:
        return 1.6


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
    graph_counter = 0
    for minute in range(start_time, maximum_time):
        water_exchange_curve[graph_counter] = {'date': minute,
                                               'value': water_exchange_calculator(stop_conc, 40,
                                                                                  (minute - start_time) / 60)}

        if water_exchange_curve[graph_counter]['value'] <= setting_curve[graph_counter]['value']:
            start_break_time = minute
            end_break_time = start_break_time + 61
            break
        graph_counter += 1
    graph_counter_break = graph_counter
    for minute in range(start_break_time + 1, end_break_time):
        water_exchange_curve[graph_counter] = {'date': minute,
                                               'value': water_exchange_curve[graph_counter_break]['value']}
        graph_counter += 1

    for minute in range(end_break_time + 1, maximum_time):
        water_exchange_curve[graph_counter] = {'date': minute,
                                               'value': water_exchange_calculator(
                                                   water_exchange_curve[graph_counter_break]['value'],
                                                   10,
                                                   (minute - end_break_time) / 60)}

        if water_exchange_curve[graph_counter]['value'] <= crit_curve[graph_counter]['value']:
            break
        graph_counter += 1
    return water_exchange_curve


def water_exchange_calculator(
        c_start: float,
        rate: float,
        time: float,
        po_pr: float = 0.992,
        po: float = 0.767,
        v: float = 338
) -> float:
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
