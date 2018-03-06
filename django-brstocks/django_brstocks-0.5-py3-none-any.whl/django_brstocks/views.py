from django.shortcuts import render


def index(request):
    return render(request, 'investments/index.html')


def stocks(request):
    return render(request, 'investments/stocks.html')
