from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.http import HttpResponse


from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse 

from . import models
from django.shortcuts import get_object_or_404

class Editor_View:

    def get_page(self):
        page = get_object_or_404(models.get_page_model(),site=self.request.page_site,slug=self.kwargs['slug'])
        return page

class Delete(TemplateView,Editor_View):
    template_name = 'page/editor_confirm_delete.html'

    def get_context_data(self, **kwargs):
        page = self.get_page()
        editor = get_object_or_404(models.Page_Editor,pk=self.kwargs['editor'])

        return {
            'editor': editor,
            'page': page 
        }


    def post(self, request, *args, **kwargs):
        page = self.get_page()
        page_editor = get_object_or_404(models.Page_Editor,pk=self.kwargs['editor'])
        if page_editor and (page_editor.page == page):
            page_editor.delete()

            if self.request.is_ajax():
                return HttpResponse('Success')
        return HttpResponseRedirect(reverse("page_edit",args=[page.slug])) 

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perm('page.delete_page_editor') :
            return HttpResponse('Sorry, You do not have rights!')
        
        return super(Delete, self).dispatch(request,*args, **kwargs)
    
    
class Add(TemplateView,Editor_View):
    template_name = 'page/editor_form.html'

    found_editors = None
    
    def get_context_data(self, **kwargs):

        return {
            'found_editors': self.found_editors 
        }

     
    def post(self, request, *args, **kwargs):
        add_editor = self.request.POST.get('add_editor')
        
        if add_editor:
            user = get_object_or_404(models.get_page_site_user(),pk=add_editor)
            page = self.get_page()
            page_editor = models.Page_Editor(editor=user,page=page)
            page_editor.save()
            if self.request.is_ajax():
                return HttpResponse('Success')
            else:
                return HttpResponseRedirect(reverse("page_edit",args=[page.slug])) 
            
        else:
            username = self.request.POST.get('username')
            first_name = self.request.POST.get('first_name')
            last_name = self.request.POST.get('last_name')
            
            q = models.get_page_site_user().get_site_users(self.request.page_site)
            if username:
                q = q.filter(username__iexact=username)
    
            if first_name:
                q = q.filter(first_name__iexact=first_name)
    
            if last_name:
                q = q.filter(last_name__iexact=last_name)
            
            self.found_editors = q
            
            return self.get(request,*args, **kwargs)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perm('page.add_page_editor') :
            return HttpResponse('Sorry, You do not have rights!')
        else:
            return super(Add, self).dispatch(request,*args, **kwargs)
