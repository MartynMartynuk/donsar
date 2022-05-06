import math
from boric_acid_concentration.calculate_function import calculator_handler


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
    time_end = int(((start_time - stop_time).days * 24) + ((start_time - stop_time).seconds / 3600))
    crit_curve = {}

    for current_time in range(0, time_end * 2 + 1):  # костыль, чтобы взять пошире на графике
        """ToDo переопределить до куда отрисовывать график"""
        crit_curve[current_time] = calculator_handler(power_before_stop,
                                                      effective_days_worked,
                                                      rod_height_before_stop,
                                                      crit_conc_before_stop,
                                                      current_time,
                                                      block_id)

    return crit_curve, stop_conc, time_end


def water_exchange_calculator(c_start, rate, time, po_pr=0.992, po=0.767, v=338):
    """
    Расчет теоретической кривой водообмена
    :param c_start: стартовая (стояночная) концентрация [г/дм3]
    :param rate: расход [т/ч]
    :param time: время водообмена
    :param po_pr: плотность продувки
    :param po: плотность раствора
    :param v: объем 1 контура
    :return: концентрация [г/дм3]
    """
    return c_start * math.exp(-(rate * po_pr) / (po * v) * time)


def water_exchange_plotter(start_time, stop_conc):
    """
    Предоставление значений критической концентрации (от времени) для отрисовки кривой водообмена
    :param start_time: время начала водообмена
    :param stop_conc: начальная концентрация (стояночная)
    """
    pass