from boric_acid_concentration.models import Album
from interpolation import *


# def function1(table1, table2, h0, t, min_day, max_day):  # x-меньшие сутки; y-большие сутки из названий таблиц
#     key = list(table1.keys())
#     for i in range(0, 12):
#         if int(key[i]) < h0:
#             h1_min = int(key[i])
#             h1_max = int(key[i - 1])
#             break
#     pp1_min = float(table1[key[i]][0].replace(',', '.'))
#     pp1_max = float(table1[key[i - 1]][0].replace(',', '.'))
#     pp1_inter = pp1_min + (h0 - h1_min) * (pp1_max - pp1_min) / (h1_max - h1_min)
#     p1 = float(table1[key[7]][0].replace(',', '.')) - pp1_inter
#
#     for i in range(0, 12):
#         if int(key[i]) < h0:
#             h2_min = int(key[i])
#             h2_max = int(key[i - 1])
#             break
#     pp2_min = float(table2[key[i]][0].replace(',', '.'))
#     pp2_max = float(table2[key[i - 1]][0].replace(',', '.'))
#     pp2_inter = pp2_min + (h0 - h2_min) * (pp2_max - pp2_min) / (h2_max - h2_min)
#     p2 = float(table2[key[7]][0].replace(',', '.')) - pp2_inter
#
#     return p1 + (t - min_day) * (p2 - p1) / (max_day - min_day)
#
#
# def function2(table, h0):
#     key = list(table.keys())
#     for i in range(1, 12):
#         if int(key[i]) < h0:
#             h_min = int(key[i])
#             h_max = int(key[i-1])
#             break
#     pp_min = float(table[key[i]][0].replace(',', '.'))
#     pp_max = float(table[key[i-1]][0].replace(',', '.'))
#     pp_inter = pp_min + (h0 - h_min) * (pp_max - pp_min) / (h_max - h_min)
#     return float(table[key[7]][0].replace(',', '.')) - pp_inter


def get_range(wide_range, mean):
    """
    Поиск ближайших минимального и минимального значений для интерполяции
    :param mean: величина, значение для которой ищем
    :param wide_range: полный диапазон значений
    :return: кортеж с ближайшими минимальным и максимальным значениями
    """
    for i in range(1, len(wide_range) + 1):
        if int(wide_range[i]) < mean:
            return int(wide_range[i]), int(wide_range[i - 1]), i  # (min, max, i)


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


def temp_effect(n0, t, block_id):
    """
    Раздел 1. Поиск суммарного эффекта реактивности по т-ре и мощности
    поиск эффекта реактивности из таблицы 5.9
    :param n0: мощность до останова
    :param t: проработано эффективных суток
    :param block_id: файл альбома
    """
    table = Album.objects.get(title='table1', block_id=block_id).content
    row_keys = list(table.keys())
    columns = [104, 100, 90, 80, 70, 60, 50, 40, 30]
    for i in range(2, 28):
        if int(row_keys[i]) > t:
            t_max = int(row_keys[i])
            t_min = int(row_keys[i - 1])
            break
    for j in range(0, 10):
        if int(columns[j]) == n0:
            break
    p_min = float(table[row_keys[i - 1]][j].replace(',', '.'))
    p_max = float(table[row_keys[i]][j].replace(',', '.'))
    return p_min + (t - t_min) * (p_max - p_min) / (t_max - t_min)


# def temp_eff(n_0, t, block_id):
#     table = Album.objects.get(title='table1', block_id=block_id).content


def group_effect(h0, t, block_id):
    """
    Раздел 2. Эффект реактивности за счет изменения положения 10й группы до 40%
    :param h0: положение 10-й группы до останова
    :param t: проработано эффективных суток
    :param block_id: файл альбома
    """
    table_start = Album.objects.get(title='table2_start', block_id=block_id).content
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


def xe_effect(t, tzap, block_id, table):
    """
    Раздел 3. Эффект реактивности, вызванный ксеноном
    :param t: проработано эффективных суток
    :param tzap: время, прошедшее с останова
    :param block_id: файл альбома
    """
    # table = Album.objects.get(title='table3', block_id=block_id).content
    key = list(table.keys())
    table_column_names = [0, 100, 200, 300, 400, 500]
    for i in range(0, 73):
        if tzap >= 72:
            i = 72
            break
        elif i > tzap:
            break
    t_zap_list = [i - 1, i]
    for j in range(0, 6):
        if table_column_names[j] > t:
            t_list = [table_column_names[j - 1], table_column_names[j]]
            break

    p_min_tzap_lst = [float(table[key[i - 1]][j - 1].replace(',', '.')),
                      float(table[key[i - 1]][j].replace(',', '.'))]
    p_max_tzap_lst = [float(table[key[i]][j - 1].replace(',', '.')),
                      float(table[key[i]][j].replace(',', '.'))]

    p_tzap_iter = [linear_interpolate_list(t, t_list, p_min_tzap_lst),
                   linear_interpolate_list(t, t_list, p_max_tzap_lst)]

    return linear_interpolate_list(tzap, t_zap_list, p_tzap_iter)


def bor_efficiency(t, block_id):
    """
    Эффективность БК
    :param t: проработано эффективных суток
    :param block_id: файл альбома
    """
    table = Album.objects.get(title='table4', block_id=block_id).content
    table_key = list(table.keys())
    for i in range(0, 27):
        if float(table_key[i].replace(',', '.')) > t:
            table4_t_max = float(table_key[i].replace(',', '.'))
            table4_t_min = float(table_key[i - 1].replace(',', '.'))
            break
    dc_max = float(table[table_key[i]][11].replace(',', '.'))
    dc_min = float(table[table_key[i - 1]][11].replace(',', '.'))
    return dc_min + (t - table4_t_min) * (dc_max - dc_min) / (table4_t_max - table4_t_min)


def conc_calc(p, c0, dc):
    """
    Определение критической концентрации БК
    :param p: компенсируемый эффект реактивности
    :param c0: начальная концентрация БК
    :param dc: эффективность БК
    """
    return c0 + p / (-dc)