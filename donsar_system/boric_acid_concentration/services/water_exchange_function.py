import math
from boric_acid_concentration.services.calculate_function import *


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
