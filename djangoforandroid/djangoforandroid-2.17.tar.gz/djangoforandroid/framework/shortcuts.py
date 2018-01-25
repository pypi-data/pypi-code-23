from django.shortcuts import render


#----------------------------------------------------------------------
def brython_render(request, template, debug=0, context={}):
    """"""

    context['brython_template'] = template
    context['debug'] = debug

    return render(request, "djangoforandroid/brythonframework/base.html", context)


