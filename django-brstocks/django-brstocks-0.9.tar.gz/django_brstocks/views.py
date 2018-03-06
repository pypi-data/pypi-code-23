from django.shortcuts import render
from django.template import Context, loader


def index(request):
    return render(request, 'investments/index.html')

def stocks(request):
    return render(request, 'investments/stocks.html')
