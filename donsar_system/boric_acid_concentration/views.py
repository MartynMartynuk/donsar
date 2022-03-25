from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from .calculate_function import *
from .forms import *
from .models import *


# Метод с использованием ModelForm
def album_upload_page(request):
    if request.method == 'POST':
        form = UploadAlbumForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
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
                                                        'Album.docx')
                # result[0] = f'Целевая стартовая концентрация БК: {round(result[0], 3)}'
                # result[1] = f'Необходимо изменить текущую концентрацию на {round(result[1], 3)}'
                result = [f'Целевая стартовая концентрация БК: {round(calculation_result[0], 3)}',
                          f'Необходимо изменить текущую концентрацию на {round(calculation_result[1], 3)}']
            except:
                print(type(BorCalculator.power_before_stop))
                print(form.cleaned_data)
                result = 'Ошибка! Не удалось запустить расчет (возможно указано неправильное имя альбома НФХ'
            return render(request, 'bor_calculator/bor_calc_page.html',
                          {'form': form, 'result': result})
    else:
        form = BorCalcForm()
    return render(request, 'bor_calculator/bor_calc_page.html', {'form': form})
