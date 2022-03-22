from django.shortcuts import render
from .forms import BorCalcForm
from .models import BorCalculator


def bor_calc_page(request):
    if request.method == 'POST':
        form = BorCalcForm(request.POST)
        if form.is_valid():
            try:
                return BorCalculator.returner(BorCalculator, BorCalculator.param_1, BorCalculator.param_2)
            except:
                form.add_error(None, 'Ошибка расчета')
    else:
        form = BorCalcForm()
    return render(request, 'bor_calc_page.html', {'form': form, 'result': BorCalculator.returner})
