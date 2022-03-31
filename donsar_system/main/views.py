from django.shortcuts import render

menu = [{'title': 'Главная', 'url_name': 'main_page'},
        {'title': 'Расчет концентрации БК', 'url_name': 'bor_calc'},
        {'title': 'Добавить альбом НФХ', 'url_name': 'add_album'},
        {'title': 'Добавить название альбома', 'url_name': 'add_album'}
        ]


def main_page(request):
    return render(request, 'main.html', {'title': 'Система ОЯБиН'})
    # return render(request, 'index.html', )#{'title': 'Система ОЯБиН', 'menu': menu})
