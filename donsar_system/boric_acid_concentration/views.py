from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import *
from .models import *
from .album_handler import *


# Метод без использования ModelForm
def album_upload_page(request):
    if request.method == 'POST':
        form = UploadAlbumForm(request.POST, request.FILES)
        if form.is_valid():
            album_handle(request.FILES['file'])
            return HttpResponseRedirect('bc/')
    else:
        form = UploadAlbumForm()
    return render(request, 'bor_calculator/album_upload_page.html', {'form': form})


# Метод с использованием ModelForm
# def album_upload_page(request):
#     if request.method == 'POST':
#         form = ModelFormWithFileField(request.POST, request.FILES)  #занести в .forms
#         if form.is_valid():
#             form.save()
#         else:
#             form = ModelFormWithFileField()
#         return render(request, 'album_upload_page.html', {'form': form})

# def bor_calc_page(request):
#     if request.method == 'POST':
#         form = BorCalcForm(request.POST)
#         if form.is_valid():
#             print(form.cleaned_data)
#         else:
#             form = BorCalcForm()
#     return render(request, 'bor_calc_page.html', {'form': form, 'result': BorCalculator.returner})
