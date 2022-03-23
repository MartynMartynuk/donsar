from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
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
            result = BorCalculator.returner(form.cleaned_data['param_1'],
                                            form.cleaned_data['param_2'])
            return render(request, 'bor_calculator/bor_calc_page.html',
                          {'form': form, 'result': result})
    else:
        form = BorCalcForm()
    return render(request, 'bor_calculator/bor_calc_page.html', {'form': form})
