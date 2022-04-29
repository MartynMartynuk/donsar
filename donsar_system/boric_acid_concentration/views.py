from django.shortcuts import render, redirect
from .calculate_function import *
from .forms import *
from .models import *
from .album_handler import *


# Метод с использованием ModelForm
def add_album_page(request):
    if request.method == 'POST':
        form = AddAlbumForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            file_name = str(request.FILES['album_file']).replace(' ', '_')
            batch_params = str(request.FILES['album_file'])[:-5].split(' ')
            block_num = batch_params[1]
            batch_num = batch_params[-1]
            try:
                Block.objects.get(block_number=block_num, batch_number=batch_num)
            except:
                Block.objects.create(block_number=block_num, batch_number=batch_num)
            block_id = Block.objects.get(block_number=block_num, batch_number=batch_num).pk
            document_obj = open_file(file_name)
            Album.objects.create(title='table1', content=handler(document_obj, 0, 2, 28, 1, 10), block_id=block_id)
            Album.objects.create(title='table2_start', content=handler(document_obj, 1, 1, 11, 1, 5), block_id=block_id)
            Album.objects.create(title='table2_100', content=handler(document_obj, 2, 1, 11, 1, 5), block_id=block_id)
            Album.objects.create(title='table2_200', content=handler(document_obj, 3, 1, 11, 1, 5), block_id=block_id)
            Album.objects.create(title='table2_300', content=handler(document_obj, 4, 1, 11, 1, 5), block_id=block_id)
            Album.objects.create(title='table2_400', content=handler(document_obj, 5, 1, 11, 1, 5), block_id=block_id)
            Album.objects.create(title='table2_500', content=handler(document_obj, 6, 1, 11, 1, 5), block_id=block_id)
            Album.objects.create(title='table2_end', content=handler(document_obj, 7, 1, 11, 1, 5), block_id=block_id)
            Album.objects.create(title='table3', content=handler(document_obj, 8, 2, 75, 1, 8), block_id=block_id),
            Album.objects.create(title='table4', content=handler(document_obj, 9, 1, 28, 1, 15), block_id=block_id)
            return redirect('bor_calc')
    else:
        form = AddAlbumForm()
    return render(request, 'bor_calculator/album_upload_page.html', {'title': 'Добавление альбома', 'form': form})


def bor_calc_page(request):
    if request.method == 'POST':
        form = BorCalcForm(request.POST)
        if form.is_valid():
            try:
                block_id = int(request.POST['block'])
                print(block_id)
                calculation_result = calculator_handler(form.cleaned_data['power_before_stop'],
                                                        form.cleaned_data['effective_days_worked'],
                                                        form.cleaned_data['rod_height_before_stop'],
                                                        form.cleaned_data['crit_conc_before_stop'],
                                                        form.cleaned_data['start_time'],
                                                        block_id)

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
    return render(request, 'bor_calculator/bor_calc_page.html', {'title': 'Расчет концентрации БК', 'form': form})
