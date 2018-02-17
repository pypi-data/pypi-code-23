import os
import datetime
import re

from django.db import models
from django.conf import settings
from django.core.cache import cache
import hashlib
from django.contrib.auth.models import User
from django.apps import apps
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist


re_alphaplus = re.compile("[^a-zA-Z0-9/\.]")
re_page_slug = re.compile('^[\w\-_/]+$')

class Invalid_Page_Name(Exception):
    pass

PAGE_SITE = getattr(settings, 'PAGE_SITE', 'page.Site')
PAGE_PAGE = getattr(settings, 'PAGE_PAGE', 'page.Page')
PAGE_USER = getattr(settings, 'PAGE_USER', 'page.Page_User')
PAGE_CACHE_EXPIRE =getattr(settings, 'PAGE_CACHE_EXPIRE', 60*60*4 ) # four hour
PAGE_PAGE_CACHE= getattr(settings, 'PAGE_PAGE_CACHE', False) # disable page_cache by default
PAGE_SITE_CACHE= getattr(settings, 'PAGE_SITE_CACHE', False) # disable page_cache by default



def get_class_model_perm(class_model,perm):
    (model_class,model) = get_class_model(PAGE_PAGE)
    perm = "%s.%s_%s" %(model_class,perm,model)
    return perm.lower()
 
def get_class_model(class_model):
    return class_model.split('.')

#monkey patch user to show fullname  Subclassing breaks manytomany deletes
def user_unicode(self):
    return self.get_full_name()

User.__unicode__ = user_unicode 

#site
def get_page_site_key(domain_name):
    return "page_site/%s" % domain_name

def get_site_model():
    return apps.get_model ( *PAGE_SITE.split('.',1) )

def get_page_site(request):
    page_site = None
    if PAGE_SITE_CACHE:#try cache
        key = get_page_site_key(request.get_host())
        page_site = cache.get(key,None)

    if page_site:
        return page_site
    else:
        page_site_model = get_site_model()
        page_site = page_site_model.get_site(request)
        if PAGE_SITE_CACHE:
            cache.set(key,page_site,PAGE_CACHE_EXPIRE)
        return page_site

def get_page_site_version_key(domain_name):
    return "page_site_version/%s" % domain_name
   
def get_page_site_version(request):
    if PAGE_PAGE_CACHE:
        key = get_page_site_version_key(request.get_host())
        return cache.get(key,0)
    else:
        return 0

def invalidate_site_cache(request):
    if PAGE_PAGE_CACHE:
        domain_name = request.get_host()
        try:
            cache.incr(get_page_site_version_key(domain_name))
        except ValueError:
            cache.set(get_page_site_version_key(domain_name),1)

        cache.delete(get_page_site_key(domain_name))
        if (request.page_site):
            cache.delete(get_page_site_key(request.page_site.domain_name))

def get_page_site_user():
    page_user =  apps.get_model ( *PAGE_USER.split('.',1) )
    return page_user

#page
def get_page_model():
    return apps.get_model ( *PAGE_PAGE.split('.',1) )

def get_page(request):
    slug = request.path[1:].lower().rstrip('/')
    if slug == "":
        slug="default"

    page = None

    if PAGE_PAGE_CACHE:
        key = get_page_key(request.page_site.pk,slug)

        if not request.GET.get('refresh') :
            page = cache.get(key,None)

    if not page:
        try:
            #print "looking for page slug %s" % slug
            page_model =  get_page_model()

            page = page_model.objects.get(slug=slug,site=request.page_site)
            #print("looking for page page %s" % slug)
            if PAGE_PAGE_CACHE:
                cache.set(key,page,PAGE_CACHE_EXPIRE)
        except ObjectDoesNotExist:
            page = None 
                
    return page


def get_page_key(site_pk,slug):
    #print "get_page slug='%s'" % slug

    if re_page_slug.match(slug) is None:
        raise Invalid_Page_Name

    #use cache if there
    key = "%s/page/%s" % (site_pk,slug)
    #key = hashlib.md5(key).hexdigest()
    return key

    
class Site_Abstract(models.Model):
    class Meta:
        abstract = True
        
    title = models.CharField(max_length = 200)
    domain_name = models.CharField(max_length = 300,primary_key=True)
    default_domain = models.BooleanField(default=False)

    meta_data = models.TextField(blank=True,null=True)
    footer = models.TextField(blank=True,null=True)

    def __str__(self):
        return self.title

    @staticmethod
    def get_site(request):
        try:
            page_site = get_site_model().objects.get(domain_name = request.get_host())
        except ObjectDoesNotExist:
            try:
                page_site = get_site_model().objects.filter(default_domain = True)[0]
            except IndexError: #create the site
                page_site = get_site_model()(domain_name = request.get_host(),title=request.get_host())
                page_site.save()
        return page_site


if PAGE_SITE == 'page.Site':
    class Site(Site_Abstract):
        pass     
    
class Page_User(User):
    class Meta:
        proxy = True
        
    @staticmethod
    def get_site_users(site):
        """overide this model and supply this function to use custom users, for example, based on site"""
        return Page_User.objects.all()



class Page_Abstract(models.Model):
    class Meta:
        abstract = True
        permissions = (
            ("change_show_in_menu", "change_show_in_menu"),
        )

    site = models.ForeignKey(PAGE_SITE)
    slug = models.CharField(max_length = 100,db_index=True)
    title = models.CharField(max_length = 100,verbose_name="Menu Title")
    show_in_menu = models.BooleanField(default=False)
    priority = models.IntegerField(default=0)
    html_title = models.CharField(max_length = 100,null=True,blank=True)
    content = models.TextField()
    members_only = models.BooleanField(default=False)
    lastmod = models.DateTimeField(default=timezone.now)
    sitemap  = models.BooleanField(default=True,verbose_name="Share a link to this page with search engines")


    def get_absolute_url(self):
        return "/%s" % self.slug

    def __str__(self):
        return self.slug

class Page_Editor(models.Model):
    page = models.ForeignKey(PAGE_PAGE,db_index=True)
    editor = models.ForeignKey(PAGE_USER,db_index=True)
    
    def __str__(self):
        return "%s %s" % (self.page,self.editor)

if PAGE_PAGE == 'page.Page':
    class Page(Page_Abstract):
        pass

class Page_Version(models.Model):
    page = models.ForeignKey(PAGE_PAGE)
    saved = models.DateTimeField(default=timezone.now)
    data = models.TextField()
    class Meta:
        ordering = ["-saved"]


    def __str__(self):
        return "%s:%s %s" % (self.page.site,self.page.slug,self.saved)

def upload_uuid_file_to(instance,filename):
    path = 'page/%s' % instance.uuid
    return get_filename(path,filename,255)

class UUID_File(models.Model):
    file = models.FileField(max_length=255,upload_to=upload_uuid_file_to)
    uuid = models.CharField(max_length=100)

    def filename(self):
        return os.path.basename(self.file.name)
    
    def __str__(self):
        return self.file.name

def get_filename(path,filename,max_len):
    dst = '%s/%s' % (path,filename)
    if len(dst) > max_len:
        dst = '%s/%s' % (path,hashlib.md5(filename).hexdigest())

    return dst


def upload_file_to(instance,filename):
#    ext = os.path.splitext(filename)[1]
#    ext = ext.lower()
    path = 'page/%s' % instance.page.pk
    return get_filename(path,filename,255)

class File(models.Model):
    file = models.FileField(max_length=255,upload_to=upload_file_to)
    page = models.ForeignKey(PAGE_PAGE,related_name = 'page_file')


    def filename(self):
        return os.path.basename(self.file.name)

    def __str__(self):
        return self.file.name


