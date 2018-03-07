import os
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from djatex import render_latex
from .forms import ArticleForm

app_base = os.path.abspath(os.path.join(settings.BASE_DIR, 'testapp'))
tex_home = os.path.join(app_base, 'tex_home')

def index(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        
        if form.is_valid():
            author = form.cleaned_data['author']
            title = form.cleaned_data['title']
            form_context={
                'form': form,
                'author': author,
                'title': title
            }
            return render_latex(request, 'testfile.pdf', 'testapp/test.tex',
                                error_template_name='testapp/error.html',
                                home_dir=tex_home, context=form_context)
    else:
        form = ArticleForm()
        context = {'form': form}
    return render(request, 'testapp/index.html', context) 

def download(request):
    context = {'author': b'Joe Blow', 'title': b'An old result'}
