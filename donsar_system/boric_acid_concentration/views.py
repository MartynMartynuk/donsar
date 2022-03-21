from django.shortcuts import render


def bor_calc_page(request):
    return render(request, template_name='bor_calc_page.html')
