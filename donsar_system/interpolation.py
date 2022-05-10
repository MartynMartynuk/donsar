import numpy as np


def linear_interpolate(x, x_knot, y_knot):
    ans = y_knot[0] + (x - x_knot[0]) * (y_knot[1] - y_knot[0]) / (x_knot[1] - x_knot[0])
    return ans


def lagrange(x, x_list, y_list):
    lagr = 0
    n = len(x_list)
    for i in range(0, n):
        chislit = 1
        znamen = 1
        for j in range(0, n):
            if i != j:
                chislit = chislit * (x - x_list[j])
                znamen = znamen * (x_list[i] - x_list[j])
        lagr = lagr + y_list[i] * chislit / znamen
    return lagr


'''выполняет интерполяцию методом кубического сплайна. применяется к списку Х'''


def splyne_interpolation(knots, function, x):
    n = len(function)
    # вычисляем шаг h
    shag = [None]
    shag = shag * (n - 1)
    for i in range(0, n - 1):
        shag[i] = knots[i + 1] - knots[i]

    # заполняем матрицу СЛАУ
    matrix = np.zeros((n, n), dtype=float)
    matrix[0, 0] = 1
    matrix[n - 1, n - 1] = 1
    j = 0
    for i in range(1, n):
        matrix[i, j] = shag[i - 1]
        matrix[i, j + 1] = 2 * (shag[i - 1] + shag[i])
        matrix[i, j + 2] = shag[i]
        j += 1
        if (j + 2) >= n:
            break

    vektor = [None]
    vektor = vektor * n
    vektor[0] = 0  # зануляю в силу того что написано в местной методичке
    vektor[n - 1] = 0  # вообще может быть и не равно 0
    for i in range(1, n - 1):
        # т.к шаги нумеруются с 0, индекс шагов пишу на 1 меньше положенного
        chast1 = (function[i + 1] - function[i]) / shag[i]
        chast2 = (function[i] - function[i - 1]) / shag[i - 1]
        vektor[i] = 3 * (chast1 - chast2)  # или 6 * ...

    coef_c = progonka(matrix, vektor)

    # вычисляем коэффициент d
    coef_d = [None]
    coef_d = coef_d * (n - 1)
    for i in range(0, n - 1):
        coef_d[i] = (coef_c[i + 1] - coef_c[i]) / (3 * shag[i])  # или 1*shag

    # вычисляем коэффициент b
    coef_b = [None]
    coef_b = coef_b * (n - 1)
    for i in range(0, n - 1):
        slag1 = (function[i + 1] - function[i]) / shag[i]
        slag2 = shag[i] / 3 * (2 * coef_c[i] + coef_c[i + 1])
        coef_b[i] = slag1 - slag2

    splyne_function = []
    for j in range(0, len(x)):
        for i in range(n - 1, -1, -1):
            if x[j] > knots[i]:
                break
        slag_a = function[i]
        slag_b = coef_b[i] * (x[j] - knots[i])
        slag_c = coef_c[i] * (x[j] - knots[i]) ** 2
        slag_d = coef_d[i] * (x[j] - knots[i]) ** 3
        splyne_function.append(slag_a + slag_b + slag_c + slag_d)
    return splyne_function


'''решает СЛАУ методом прогонки'''


def progonka(matrix, vektor):
    # вычисляем размерность матрицы с учетом счета с 0
    n = len(matrix) - 1

    alpha = [None]
    alpha = alpha * n
    beta = [None]
    beta = beta * n
    reshen = [None]
    reshen = reshen * (n + 1)

    alpha[0] = -matrix[0, 1]
    beta[0] = vektor[0]

    c_pos = 2
    str_pos = 1
    # Прямой ход прогонки
    for i in range(1, n):
        chislitel = -matrix[str_pos, c_pos]
        znamen1 = alpha[i - 1] * matrix[str_pos, c_pos - 2]
        znamen2 = matrix[str_pos, c_pos - 1]
        alpha[i] = chislitel / (znamen1 + znamen2)

        chislitel = vektor[str_pos] - matrix[str_pos, c_pos - 2] * beta[i - 1]
        beta[i] = chislitel / (znamen1 + znamen2)
        c_pos += 1
        str_pos += 1
    # Обратный ход прогонки
    reshen[n] = (-matrix[n, n - 1] * beta[n - 1] + vektor[n]) / (1 - (-matrix[n, n - 1] * alpha[n - 1]))
    for i in range(n - 1, -1, -1):
        reshen[i] = alpha[i] * reshen[i + 1] + beta[i]
    # Ответ (возвращает список)
    return reshen


'''экстраполирует заданную по узлам функцию путем добавления узловых точек 
    и поиска значений в них используя вычисления по полиному Лагранжа'''


def extrapolation_with_lagr(knots, function, knots_dop):
    # создает словарь для новых x со значениями lagr
    func_dop = {}
    for i in knots_dop:
        func_dop[i] = lagrange(i, knots, function)

    # добавляет точки в массив узлов и функций
    for key in func_dop:
        if key > knots[len(knots) - 1]:
            knots.append(key)
            function.append(func_dop[key])
        else:
            for i in knots:
                if key < i:
                    knots.insert(knots.index(i), key)
                    function.insert(knots.index(i) - 1, func_dop[key])
                    break
    x_new = np.linspace(knots[0], knots[len(knots) - 1], len(knots) * 20)

    # применяет интерполяцию сплайнами к расширеной сетке узлов
    return x_new, splyne_interpolation(knots, function, x_new)


'''выполняет интерполяцию методом кубического сплайна. применяется к списку Х'''


def splyne_function(knots, function, x):
    n = len(function)
    # вычисляем шаг h
    shag = [None]
    shag = shag * (n - 1)
    for i in range(0, n - 1):
        shag[i] = knots[i + 1] - knots[i]

    # заполняем матрицу СЛАУ
    matrix = np.zeros((n, n), dtype=float)
    matrix[0, 0] = 1
    matrix[n - 1, n - 1] = 1
    j = 0
    for i in range(1, n):
        matrix[i, j] = shag[i - 1]
        matrix[i, j + 1] = 2 * (shag[i - 1] + shag[i])
        matrix[i, j + 2] = shag[i]
        j += 1
        if (j + 2) >= n:
            break

    vektor = [None]
    vektor = vektor * n
    vektor[0] = 0  # зануляю в силу того что написано в местной методичке
    vektor[n - 1] = 0  # вообще может быть и не равно 0
    for i in range(1, n - 1):
        # т.к шаги нумеруются с 0, индекс шагов пишу на 1 меньше положенного
        chast1 = (function[i + 1] - function[i]) / shag[i]
        chast2 = (function[i] - function[i - 1]) / shag[i - 1]
        vektor[i] = 3 * (chast1 - chast2)  # или 6 * ...

    coef_c = progonka(matrix, vektor)

    # вычисляем коэффициент d
    coef_d = [None]
    coef_d = coef_d * (n - 1)
    for i in range(0, n - 1):
        coef_d[i] = (coef_c[i + 1] - coef_c[i]) / (3 * shag[i])  # или 1*shag

    # вычисляем коэффициент b
    coef_b = [None]
    coef_b = coef_b * (n - 1)
    for i in range(0, n - 1):
        slag1 = (function[i + 1] - function[i]) / shag[i]
        slag2 = shag[i] / 3 * (2 * coef_c[i] + coef_c[i + 1])
        coef_b[i] = slag1 - slag2

    for i in range(n - 1, -1, -1):
        if x > knots[i]:
            break
    slag_a = function[i]
    slag_b = coef_b[i] * (x - knots[i])
    slag_c = coef_c[i] * (x - knots[i]) ** 2
    slag_d = coef_d[i] * (x - knots[i]) ** 3
    splyne_function = (slag_a + slag_b + slag_c + slag_d)
    return splyne_function
