from docx import Document
from donsar_system.settings import MEDIA_ROOT


def function1(table1, table2, h0, t, min_day, max_day):  # x-меньшие сутки; y-большие сутки из названий таблиц
    key = list(table1.keys())
    for i in range(0, 12):
        if int(key[i]) < h0:
            h1_min = int(key[i])
            h1_max = int(key[i - 1])
            break
    pp1_min = float(table1[key[i]][0].replace(',', '.'))
    pp1_max = float(table1[key[i - 1]][0].replace(',', '.'))
    pp1_inter = pp1_min + (h0 - h1_min) * (pp1_max - pp1_min) / (h1_max - h1_min)
    p1 = float(table1[key[7]][0].replace(',', '.')) - pp1_inter

    for i in range(0, 12):
        if int(key[i]) < h0:
            h2_min = int(key[i])
            h2_max = int(key[i - 1])
            break
    pp2_min = float(table2[key[i]][0].replace(',', '.'))
    pp2_max = float(table2[key[i - 1]][0].replace(',', '.'))
    pp2_inter = pp2_min + (h0 - h2_min) * (pp2_max - pp2_min) / (h2_max - h2_min)
    p2 = float(table2[key[7]][0].replace(',', '.')) - pp2_inter

    return p1 + (t - min_day) * (p2 - p1) / (max_day - min_day)


def function2(table, h0):
    key = list(table.keys())
    for i in range(1, 12):
        if int(key[i]) < h0:
            h_min = int(key[i])
            h_max = int(key[i-1])
            break
    pp_min = float(table[key[i]][0].replace(',', '.'))
    pp_max = float(table[key[i-1]][0].replace(',', '.'))
    pp_inter = pp_min + (h0 - h_min) * (pp_max - pp_min) / (h_max - h_min)
    return float(table[key[7]][0].replace(',', '.')) - pp_inter


def calculator_handler(n0, t, h0, c0, tzap, file_name,
                       table1_rows, table1_columns, table2_start, table2_100,
                       table2_200, table2_300, table2_400, table2_500, table2_end,
                       table3):
    docum = Document(MEDIA_ROOT + '/' + file_name)

    # Раздел 1. Поиск суммарного эффекта реактивности по т-ре и мощности
    # поиск эффекта реактивности из таблицы 5.9
    row_keys = list(table1_rows.keys())
    column_keys = list(table1_columns.keys())
    for i in range(2, 28):
        if int(row_keys[i]) > t:
            tmax = int(row_keys[i])
            tmin = int(row_keys[i - 1])
            break
    for j in range(0, 10):
        if int(column_keys[j]) == n0:
            break
    p1_min = float(table1_rows[row_keys[i-1]][j].replace(',', '.'))
    p1_max = float(table1_rows[row_keys[i]][j].replace(',', '.'))
    p1 = p1_min + (t - tmin) * (p1_max - p1_min) / (tmax - tmin)

    # Раздел 2. Поиск эффекта реактивности за счет изменения положения 10й группы до 40%
    if t < 100:
        table21 = table2_start
        table22 = table2_100
        p2 = function1(table21, table22, h0, t, 0, 100)
    elif t == 100:
        table21 = table2_100
        p2 = function2(table21, h0)
    elif 100 < t < 200:
        table21 = table2_100
        table22 = table2_200
        p2 = function1(table21, table22, h0, t, 100, 200)
    elif t == 200:
        table21 = table2_200
        p2 = function2(table21, h0)
    elif 200 < t < 300:
        table21 = table2_200
        table22 = table2_300
        p2 = function1(table21, table22, h0, t, 200, 300)
    elif t == 300:
        table21 = table2_300
        p2 = function2(table21, h0)
    elif 300 < t < 400:
        table21 = table2_300
        table22 = table2_400
        p2 = function1(table21, table22, h0, t, 300, 400)
    elif t == 400:
        table21 = table2_400
        p2 = function2(table21, h0)
    elif 400 < t < 500:
        table21 = table2_400
        table22 = table2_500
        p2 = function1(table21, table22, h0, t, 400, 500)
    elif t == 500:
        table21 = table2_500
        p2 = function2(table21, h0)
    elif t > 500:
        table21 = table2_500
        table22 = table2_end
        p2 = function1(table21, table22, h0, t, 500, 550)  # ?????-вопрос о большем времени

    # Раздел 3. Эффект реактивности, вызванный ксеноном
    key = list(table3.keys())
    table3_column_names = [0, 100, 200, 300, 400, 500]
    for i in range(0, 73):
        if int(key[i]) == tzap:
            break
        elif tzap > 72:
            i = 74

    for j in range(0, 6):
        if table3_column_names[j] > t:
            t_max = table3_column_names[j]
            t_min = table3_column_names[j-1]
            break
    p3_min = float(table3[key[i]][j-1].replace(',', '.'))
    p3_max = float(table3[key[i]][j].replace(',', '.'))

    p3 = p3_min + (t - tmin) * (p3_max - p3_min) / (tmax - tmin)

    # Раздел 3+. Общая реактивность
    ptot = p1 + p2 + p3

    # Раздел 4. Эффективность БК
    table4 = docum.tables[9]
    for i in range(1, 28):
        if float(table4.rows[i].cells[0].text.strip().replace(',', '.')) > t:
            tmax = float(table4.rows[i].cells[0].text.strip().replace(',', '.'))
            tmin = float(table4.rows[i - 1].cells[0].text.strip().replace(',', '.'))
            break

    dcmax = float(table4.rows[i].cells[12].text.strip().replace(',', '.'))
    dcmin = float(table4.rows[i - 1].cells[12].text.strip().replace(',', '.'))
    dc = dcmin + (t - tmin) * (dcmax - dcmin) / (tmax - tmin)

    # Раздел 5. Определение дельта С и Скрит
    deltac = ptot / (-dc)
    # print('deltac=', deltac)
    ckrit = c0 + deltac
    # print('Cкрит=', ckrit)
    return ckrit, deltac


# if __name__ == '__main__':
#     print('!!!', round(calculator_handler(446, 104, 89, 20, 1.22, 'Album.docx'), 4))
