import math
from boric_acid_concentration.models import Album
from boric_acid_concentration.services.interpolation import *


def get_range(wide_range, mean, compare=1, int_=True):
    """
    Поиск ближайших минимального и минимального значений для интерполяции
    :param mean: величина, значение для которой ищем
    :param wide_range: полный диапазон значений
    :param compare: параметр сравнения: 1 - ключ меньше значения, 2 - ключ больше значения, ключ равен значению
    :param int_: параметр преобразования в int или float
    :return: кортеж с ближайшими минимальным и максимальным значениями
    """
    if int_ is True:
        if compare == 1:
            for i in range(0, len(wide_range) + 1):
                if int(wide_range[i]) <= mean:
                    return int(wide_range[i]), int(wide_range[i-1]), i  # (min, max, i)
        elif compare == 2:
            for i in range(0, len(wide_range) + 1):
                if int(wide_range[i]) >= mean:
                    return int(wide_range[i-1]), int(wide_range[i]), i  # (min, max, i)
        else:
            for i in range(0, len(wide_range) + 1):
                if wide_range[i] == mean:
                    return i
    else:
        for i in range(0, len(wide_range) + 1):
            if float(wide_range[i].replace(',', '.')) > mean:
                return float(wide_range[i].replace(',', '.')), float(wide_range[i - 1].replace(',', '.')), i  # (min, max, i)


def suz_effect_short(table, h_0):
    """
    Расчет эффекта реактивности от движения 10-й гр. СУЗ
    :param table: таблица (словарь)
    :param h_0: высота 10-й гр. до останова
    """
    keys = list(table.keys())
    h_min, h_max, i = get_range(keys, h_0)
    p_min = float(table[keys[i]][0].replace(',', '.'))
    p_max = float(table[keys[i - 1]][0].replace(',', '.'))
    p_iter = linear_interpolate(h_0, h_min, h_max, p_min, p_max)
    return float(table[keys[7]][0].replace(',', '.')) - p_iter


def suz_effect_long(table1, table2, h_0, t, min_day, max_day):
    """
    Расчет эффекта реактивности от движения 10-й гр. СУЗ (для 2-х таблиц)
    :param table1: таблица меньшего времени (словарь)
    :param table2: таблица большего времени (словарь)
    :param h_0: высота 10-й гр. до останова
    :param t: сутки останова
    :param min_day: меньшие сутки из названий таблиц
    :param max_day: большие сутки из названий таблиц
    """
    p_1 = suz_effect_short(table1, h_0)
    p_2 = suz_effect_short(table2, h_0)
    return linear_interpolate(t, min_day, max_day, p_2, p_1)


def temp_effect(n_0, t, block_id):
    """
       Раздел 1. Поиск суммарного эффекта реактивности по т-ре и мощности
       поиск эффекта реактивности из таблицы 5.9
       :param n_0: мощность до останова
       :param t: проработано эффективных суток
       :param block_id: файл альбома
    """
    table = Album.objects.get(title='table1', block_id=block_id).content  # добавить еще КК
    days = list(table.keys())
    columns = [104, 100, 90, 80, 70, 60, 50, 40, 30]
    t_min, t_max, i = get_range(days, t, compare=2)
    j = get_range(columns, n_0, compare=3)
    p_min = float(table[days[i - 1]][j].replace(',', '.'))
    p_max = float(table[days[i]][j].replace(',', '.'))
    return linear_interpolate(t, t_min, t_max, p_min, p_max)


def group_effect(h0, t, block_id):
    """
    Раздел 2. Эффект реактивности за счет изменения положения 10й группы до 40%
    :param h0: положение 10-й группы до останова
    :param t: проработано эффективных суток
    :param block_id: файл альбома
    """
    table_start = Album.objects.get(title='table2_start', block_id=block_id).content  # возможно добавить еще КК
    table_100 = Album.objects.get(title='table2_100', block_id=block_id).content
    table_200 = Album.objects.get(title='table2_200', block_id=block_id).content
    table_300 = Album.objects.get(title='table2_300', block_id=block_id).content
    table_400 = Album.objects.get(title='table2_400', block_id=block_id).content
    table_500 = Album.objects.get(title='table2_500', block_id=block_id).content
    table_end = Album.objects.get(title='table2_end', block_id=block_id).content

    if t < 100:
        p = suz_effect_long(table_start, table_100, h0, t, 0, 100)
    elif t == 100:
        p = suz_effect_short(table_100, h0)
    elif 100 < t < 200:
        p = suz_effect_long(table_100, table_200, h0, t, 100, 200)
    elif t == 200:
        p = suz_effect_short(table_200, h0)
    elif 200 < t < 300:
        p = suz_effect_long(table_200, table_300, h0, t, 200, 300)
    elif t == 300:
        p = suz_effect_short(table_300, h0)
    elif 300 < t < 400:
        p = suz_effect_long(table_300, table_400, h0, t, 300, 400)
    elif t == 400:
        p = suz_effect_short(table_400, h0)
    elif 400 < t < 500:
        p = suz_effect_long(table_400, table_500, h0, t, 400, 500)
    elif t == 500:  # не срабатывает, надо писать доп условия во всех циклах, пока поставил заглушку в форме
        p = suz_effect_short(table_500, h0)
    # elif t > 500:  # не срабатывает, надо писать доп условия во всех циклах, пока поставил заглушку в форме
    else:
        p = suz_effect_long(table_500, table_end, h0, t, 500, 550)  # ?????-вопрос о большем времени
    return p


def xe_effect(t, t_zap, table):
    """
    Раздел 3. Эффект реактивности, вызванный ксеноном
    :param t: проработано эффективных суток
    :param t_zap: время, прошедшее с останова
    :param table: словарь таблицы
    """
    time = list(table.keys())
    columns = [0, 100, 200, 300, 400, 500]  # добавить ещё КК

    day_min, day_max, j = get_range(columns, t, 2)

    if t_zap >= 72:
        i = 72
        p_min_day = float(table[time[i]][j - 1].replace(',', '.'))
        p_max_day = float(table[time[i]][j].replace(',', '.'))
        return linear_interpolate(t, day_min, day_max, p_min_day, p_max_day)
    else:
        t_zap_min, t_zap_max, i = get_range(time, t_zap, compare=2)

        p_min_tzap_lst = [float(table[time[i - 1]][j - 1].replace(',', '.')),
                          float(table[time[i - 1]][j].replace(',', '.'))]
        p_max_tzap_lst = [float(table[time[i]][j - 1].replace(',', '.')),
                          float(table[time[i]][j].replace(',', '.'))]

        p_tzap_iter = [linear_interpolate_list(t, [day_min, day_max], p_min_tzap_lst),
                       linear_interpolate_list(t, [day_min, day_max], p_max_tzap_lst)]

        return linear_interpolate_list(t_zap, [t_zap_min, t_zap_max], p_tzap_iter)


def bor_efficiency(t, block_id):
    """
    Эффективность БК
    :param t: проработано эффективных суток
    :param block_id: файл альбома
    """
    table = Album.objects.get(title='table4', block_id=block_id).content
    days = list(table.keys())
    day_min, day_max, i = get_range(days, t, int_=False)
    dc_max = float(table[days[i]][11].replace(',', '.'))
    dc_min = float(table[days[i - 1]][11].replace(',', '.'))
    return linear_interpolate(t, day_min, day_max, dc_min, dc_max)


def conc_calc(p: float, c0: float, dc: float) -> float:
    """
    Определение критической концентрации БК
    :param p: компенсируемый эффект реактивности
    :param c0: начальная концентрация БК
    :param dc: эффективность БК
    """
    return c0 + p / (-dc)


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
