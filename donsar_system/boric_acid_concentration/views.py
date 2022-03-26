from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from .calculate_function import *
from .forms import *
from .models import *
from .album_handler import *


# Метод с использованием ModelForm
def album_upload_page(request):
    if request.method == 'POST':
        form = UploadAlbumForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            Album.objects.create(title='table1_rows', content=handler(open_file('Album.docx'), 0, 2, 28, 1, 10))
            Album.objects.create(title='table1_columns',
                                 content=handler(open_file('Album.docx'), 0, 2, 28, 1, 10, 1, True))
            Album.objects.create(title='table2_start', content=handler(open_file('Album.docx'), 1, 1, 11, 1, 5))
            Album.objects.create(title='table2_100', content=handler(open_file('Album.docx'), 2, 1, 11, 1, 5))
            Album.objects.create(title='table2_200', content=handler(open_file('Album.docx'), 3, 1, 11, 1, 5))
            Album.objects.create(title='table2_300', content=handler(open_file('Album.docx'), 4, 1, 11, 1, 5))
            Album.objects.create(title='table2_400', content=handler(open_file('Album.docx'), 5, 1, 11, 1, 5))
            Album.objects.create(title='table2_500', content=handler(open_file('Album.docx'), 6, 1, 11, 1, 5))
            Album.objects.create(title='table2_end', content=handler(open_file('Album.docx'), 7, 1, 11, 1, 5))
            Album.objects.create(title='table3', content=handler(open_file('Album.docx'), 8, 2, 75, 1, 8)),
            Album.objects.create(title='table4', content=handler(open_file('Album.docx'), 9, 1, 28, 1, 15))
            return redirect('bor_calc')
    else:
        form = UploadAlbumForm()
    return render(request, 'bor_calculator/album_upload_page.html', {'form': form})


def bor_calc_page(request):
    if request.method == 'POST':
        form = BorCalcForm(request.POST)
        if form.is_valid():
            try:
                calculation_result = calculator_handler(form.cleaned_data['power_before_stop'],
                                                        form.cleaned_data['effective_days_worked'],
                                                        form.cleaned_data['rod_height_before_stop'],
                                                        form.cleaned_data['crit_conc_before_stop'],
                                                        form.cleaned_data['start_time'],
                                                        'Album.docx',
                                                        Album.objects.get(title='table1_rows').content,
                                                        Album.objects.get(title='table1_columns').content,
                                                        Album.objects.get(title='table2_start').content,
                                                        Album.objects.get(title='table2_100').content,
                                                        Album.objects.get(title='table2_200').content,
                                                        Album.objects.get(title='table2_300').content,
                                                        Album.objects.get(title='table2_400').content,
                                                        Album.objects.get(title='table2_500').content,
                                                        Album.objects.get(title='table2_end').content,
                                                        Album.objects.get(title='table3').content,
                                                        Album.objects.get(title='table4').content)

                result = [f'Целевая стартовая концентрация БК: {round(calculation_result[0], 3)}',
                          f'Необходимо изменить текущую концентрацию на {round(calculation_result[1], 3)}']
            except:
                result = 'Ошибка! Не удалось запустить расчет (возможно указано неправильное имя альбома НФХ'
                return (request, 'bor_calculator/bor_calc_page.html',
                        {'form': form, 'result': result})
            return render(request, 'bor_calculator/bor_calc_page.html',
                          {'form': form, 'result': result})
    else:
        form = BorCalcForm()
    return render(request, 'bor_calculator/bor_calc_page.html', {'form': form})
