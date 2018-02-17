from . import models

def site_context(request):
    context = {}
    context['template'] = 'desktop.html'
    
    context['menus'] = models.get_page_model().objects.filter(show_in_menu=True).order_by('-priority','title')
    if request.META['REMOTE_ADDR'] == '127.0.0.1':
        context['DEV_SERVER'] =True
    else:
        context['DEV_SERVER'] = False 

    if hasattr(request,'page'):
        context['page'] = request.page

    if hasattr(request,'page_site'):
        context['page_site'] = request.page_site

    return context