from docx import Document
from donsar_system.settings import MEDIA_ROOT


def function1(table21, table22, h0, t, x, y):  # x-меньшие сутки; y-большие сутки из названий таблиц
    for i in range(1, 12):
        if int(table21.rows[i].cells[0].text.strip()) < h0:
            hmin1 = int(table21.rows[i].cells[0].text.strip())
            hmax1 = int(table21.rows[i - 1].cells[0].text.strip())
            break
    ppmin1 = float(table21.rows[i].cells[1].text.strip().replace(',', '.'))
    ppmax1 = float(table21.rows[i - 1].cells[1].text.strip().replace(',', '.'))
    ppinter1 = ppmin1 + (h0 - hmin1) * (ppmax1 - ppmin1) / (hmax1 - hmin1)
    p21 = float(table21.rows[7].cells[1].text.strip().replace(',', '.')) - ppinter1

    for i in range(1, 12):
        if int(table22.rows[i].cells[0].text.strip()) < h0:
            hmin2 = int(table22.rows[i].cells[0].text.strip())
            hmax2 = int(table22.rows[i - 1].cells[0].text.strip())
            break
    ppmin2 = float(table22.rows[i].cells[1].text.strip().replace(',', '.'))
    ppmax2 = float(table22.rows[i - 1].cells[1].text.strip().replace(',', '.'))
    ppinter2 = ppmin2 + (h0 - hmin2) * (ppmax2 - ppmin2) / (hmax2 - hmin2)
    p22 = float(table22.rows[7].cells[1].text.strip().replace(',', '.')) - ppinter2
    p2 = p21 + (t - x) * (p22 - p21) / (y - x)
    return p2


def function2(table21, h0):
    for i in range(1, 12):
        if int(table21.rows[i].cells[0].text.strip()) < h0:
            hmin = int(table21.rows[i].cells[0].text.strip())
            hmax = int(table21.rows[i - 1].cells[0].text.strip())
            break
    ppmin = float(table21.rows[i].cells[1].text.strip().replace(',', '.'))
    ppmax = float(table21.rows[i - 1].cells[1].text.strip().replace(',', '.'))
    ppinter = ppmin + (h0 - hmin) * (ppmax - ppmin) / (hmax - hmin)
    p2 = float(table21.rows[7].cells[1].text.strip().replace(',', '.')) - ppinter
    return p2


def calculator_handler(n0, t, h0, c0, tzap, file_name):
    docum = Document(MEDIA_ROOT + '/' + file_name)

    # Раздел 1. Поиск суммарного эффекта реактивности по т-ре и мощности
    # поиск эффекта реактивности из таблицы 5.9
    table1 = docum.tables[0]
    for i in range(2, 28):
        if int(table1.rows[i].cells[0].text.strip()) > t:
            tmax = int(table1.rows[i].cells[0].text.strip())
            tmin = int(table1.rows[i - 1].cells[0].text.strip())
            break
    for j in range(1, 10):
        if int(table1.rows[1].cells[j].text.strip()) == n0:
            break
    p1min = float(table1.rows[i - 1].cells[j].text.strip().replace(',', '.'))
    p1max = float(table1.rows[i].cells[j].text.strip().replace(',', '.'))
    p1 = p1min + (t - tmin) * (p1max - p1min) / (tmax - tmin)

    # Раздел 2. Поиск эффекта реактивности за счет изменения положения 10й группы до 40%
    if t < 100:
        table21 = docum.tables[1]
        table22 = docum.tables[2]
        p2 = function1(table21, table22, h0, t, 0, 100)
    elif t == 100:
        table21 = docum.tables[2]
        p2 = function2(table21, h0)
    elif 100 < t < 200:
        table21 = docum.tables[2]
        table22 = docum.tables[3]
        p2 = function1(table21, table22, h0, t, 100, 200)
    elif t == 200:
        table21 = docum.tables[3]
        p2 = function2(table21, h0)
    elif 200 < t < 300:
        table21 = docum.tables[3]
        table22 = docum.tables[4]
        p2 = function1(table21, table22, h0, t, 200, 300)
    elif t == 300:
        table21 = docum.tables[4]
        p2 = function2(table21, h0)
    elif 300 < t < 400:
        table21 = docum.tables[4]
        table22 = docum.tables[5]
        p2 = function1(table21, table22, h0, t, 300, 400)
    elif t == 400:
        table21 = docum.tables[5]
        p2 = function2(table21, h0)
    elif 400 < t < 500:
        table21 = docum.tables[5]
        table22 = docum.tables[6]
        p2 = function1(table21, table22, h0, t, 400, 500)
    elif t == 500:
        table21 = docum.tables[6]
        p2 = function2(table21, h0)
    elif t > 500:
        table21 = docum.tables[6]
        table22 = docum.tables[7]
        p2 = function1(table21, table22, h0, t, 500, 550)  # ?????-вопрос о большем времени

    # Раздел 3. Эффект реактивности, вызванный ксеноном
    table3 = docum.tables[8]
    for i in range(2, 75):
        if int(table3.rows[i].cells[0].text.strip()) == tzap:
            break
        elif tzap > 72:  # ???
            i = 74
            # k = input('Нажмите Enter для выхода')
            # raise MyExep("Данный случай не рассматривается, обратитесь в ОЯБиН")

    for j in range(1, 7):
        if int(table3.rows[1].cells[j].paragraphs[0].text.strip()) > t:
            tmax = int(table3.rows[1].cells[j].paragraphs[0].text.strip())
            tmin = int(table3.rows[1].cells[j - 1].paragraphs[0].text.strip())

    p3min = float(table3.rows[i].cells[j - 1].text.strip().replace(',', '.'))
    p3max = float(table3.rows[i].cells[j].text.strip().replace(',', '.'))

    p3 = p3min + (t - tmin) * (p3max - p3min) / (tmax - tmin)

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
