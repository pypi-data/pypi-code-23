from django.core.urlresolvers import reverse
from django.forms import ModelForm
import django.forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit,Field,Layout,ButtonHolder,Fieldset,HTML,Div,Hidden

from django.utils.encoding import smart_text
from django.core.exceptions import ValidationError
import re
from . import models

BUTTONS = Layout (
              ButtonHolder(
                Submit('submit', 'Save',css_id='save_button'),
                Submit('submit', 'Save and Close',css_id='save_close_button'),
                HTML('&#160;<a href="/{{object.slug}}" class="btn btn-danger" " >Close</a>')
                )
          )

slug_re = re.compile(r'^[-/\w]+$')
class Site(ModelForm):
    class Meta:
        model = models.get_site_model()
        exclude = ()
        
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.render_unmentioned_fields=True
        self.helper.layout = Layout(
            Fieldset(
                     'Edit {{ object }}',
                     'title',
                     'domain_name',
                     'default_domain',
                     'meta_data',
                     'footer',
                     ),
           BUTTONS
        )
        super(Site, self).__init__(*args,**kwargs)

class Page_Abstract(ModelForm):
    file = django.forms.FileField(required=False)
    
    class Meta:
        model = models.get_page_model()
        fields = ['slug','title','members_only','content','html_title','sitemap']
        abstract=True
        
    def __init__(self, *args, **kwargs):
        self.site = kwargs.pop('site')
        super(Page_Abstract, self).__init__(*args,**kwargs)

        self.helper = FormHelper(self)
#        self.helper.form_class = 'form-horizontal'
#        self.helper.label_class = 'col-lg-2'
#        self.helper.field_class = 'col-lg-8'
        self.helper.form_id = 'page_edit_form'
        self.helper.attrs['novalidate'] = True

        self.page_options =Layout(
            Field(Hidden('uuid', '{{ uuid }}')),
            Fieldset(
                     'Edit {{ request.GET.slug}}',
                     'slug',
                     'title',
                     'html_title',
                     'members_only',
                     'sitemap'
                     )
                                 
                )
        self.file_layout = Layout (
                                   
                        Fieldset(
                         'Files',
                          'file',
                          HTML("{% include \"page/file_upload.html\" %}"),
                          
                          ),
                       )
        

        self.helper.layout = Layout(
                 self.page_options,
                 'content',
                 self.file_layout,
                HTML("<br />"),
               BUTTONS
        )
        
    def clean_slug(self):
        slug = self.cleaned_data['slug'].lower()

        if not slug_re.search(smart_text(slug)):
            raise ValidationError("Enter a valid 'slug' consisting of letters, numbers, underscores, slashes or hyphens.")

        slug = slug.rstrip('/')
        if slug != self.instance.slug and models.get_page_model().objects.filter(site=self.site,slug=slug).exists():
            raise ValidationError("Sorry that name is already taken")
        
        return slug

class Page(Page_Abstract):
    pass

class Page_Show_In_Menu(Page_Abstract):
    class Meta:
        model = models.get_page_model()
        fields = ['slug','title','members_only','priority','content','show_in_menu','html_title','sitemap']
        
    def __init__(self, *args, **kwargs):
        super(Page_Show_In_Menu, self).__init__(*args,**kwargs)
        self.helper.layout = Layout(
                 self.page_options,
                 'show_in_menu',
                 'priority',
                 'content',
                 self.file_layout,
                 HTML("<br />"),
                 BUTTONS 
        )
