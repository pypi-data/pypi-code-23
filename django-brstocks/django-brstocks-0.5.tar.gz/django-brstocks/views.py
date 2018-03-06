from django.shortcuts import render
from django.template import Context, loader

#
def index(request):
	#books_list = Books.objects.all()
	t = loader.get_template('investments/index.html')
	#c = Context({'books_list': books_list,})
	return HttpResponse(t.render())


#def index(request):

#    return render(request, 'investments/index.html')


def stocks(request):
    return render(request, 'investments/stocks.html')
