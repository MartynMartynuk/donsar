from boric_acid_concentration.calculate_function import calculator_handler


def critical_curve_calculator(power_before_stop, effective_days_worked, rod_height_before_stop,
                              crit_conc_before_stop, block_id):
    """ Рассчитывает пусковые концентрации БК с шагом 1 минута
    :param power_before_stop:
    :param effective_days_worked:
    :param rod_height_before_stop:
    :param crit_conc_before_stop:
    :param block_id:
    """

    # время завершения ксенонового процесса
    time_end = 72
    crit_curve = {}

    for i in range(0, time_end+1):
        # время в часах после останова реактора
        current_time = i
        crit_curve[i] = calculator_handler(power_before_stop,
                                           effective_days_worked,
                                           rod_height_before_stop,
                                           crit_conc_before_stop,
                                           current_time,
                                           block_id)[0]

    # print(crit_curve)
    return crit_curve
