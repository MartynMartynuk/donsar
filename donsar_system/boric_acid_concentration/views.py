from django.shortcuts import render
from .models import BorCalculator


def bor_calc_page(request):
    return render(request, 'bor_calc_page.html', {'result': BorCalculator.returner()})
