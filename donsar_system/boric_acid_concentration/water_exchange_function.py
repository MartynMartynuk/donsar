import math

from boric_acid_concentration.calculate_function import calculator_handler


def critical_curve_calculator(power_before_stop, effective_days_worked, rod_height_before_stop,
                              crit_conc_before_stop, stop_time, start_time, block_id, stop_conc):
    """ Рассчитывает пусковые концентрации БК с шагом 1 минута
    :param stop_conc:
    :param power_before_stop:
    :param effective_days_worked:
    :param rod_height_before_stop:
    :param crit_conc_before_stop:
    :param stop_time:
    :param start_time:
    :param block_id:
    """

    # время завершения ксенонового процесса
    time_end = int(((start_time - stop_time).days * 24) + ((start_time - stop_time).seconds / 3600))
    print('!@#', time_end)
    crit_curve = {}

    for i in range(0, time_end*2+1):
        # время в часах после останова реактора
        current_time = i
        crit_curve[i] = calculator_handler(power_before_stop,
                                           effective_days_worked,
                                           rod_height_before_stop,
                                           crit_conc_before_stop,
                                           current_time,
                                           block_id)[0]

    # print(crit_curve)

    return crit_curve, stop_conc, time_end


def water_exchange_handler(c_start, rate, time, po_pr=0.992, po=0.767, v=338):

    return c_start * math.exp(-(rate * po_pr) / (po * v) * time)

