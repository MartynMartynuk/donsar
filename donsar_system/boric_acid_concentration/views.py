from django.shortcuts import render
from .forms import BorCalcForm
from .models import BorCalculator


def bor_calc_page(request):
    if request.method == 'POST':
        form = BorCalcForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
    else:
        form = BorCalcForm()
    form = BorCalcForm()
    return render(request, 'bor_calc_page.html', {'form': form, 'result': BorCalculator.returner()})
