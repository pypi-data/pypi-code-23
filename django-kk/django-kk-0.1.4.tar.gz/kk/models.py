from .article.models import *
from .base.models import *
from .gallery.models import *
from .text.models import *
from .uploads.models import *


#import os, sys, pprint
#from importlib import import_module, invalidate_caches
#script_name = os.path.basename(__file__).split('.')[0];
#.= os.path.join(os.path.dirname(os.path.abspath(__file__)), .);
#
#print('—————————————————————— ' + script_name)
#
#for module in os.listdir.:
#    if (module[0] == '_'):
#        continue
#
#    module_path = os.path.join. module)
#
#    if (not os.path.isdir(module_path)):
#        continue
#
#    script_path = os.path.join(module_path, script_name + '.py')
#
#    if (not os.path.isfile(script_path)):
#        continue
#
#    full_name = '.' + module + '.' + script_name
#    mod = import_module(full_name, __package__)
#    print(full_name)
#    print(dir(mod))
#    print('----------')
#
#print('——————————————————————')
#
#print('—asdasdasdadasdasd——————')
#print(dir())

#from .text.models import *

#pprint.pprint(sys.
#pprint.pprint(SimpleText)


#__all__ ==

#import datetime
#
#from django.db import models
#from ckeditor_uploader.fields import RichTextUploadingField
#from ckeditor.fields import RichTextField
#from sorl.thumbnail import ImageField, get_thumbnail


#class SimplePriceLists(KenzoUpload):
#    name = models.CharField(
#        'Название',
##        default = 'noname',
#        max_length = 128,
#    )
#
#    def __str__(self):
#        return self.name
#
#    class Meta:
#        abstract = True
#        verbose_name = 'прайс-лист'
#        verbose_name_plural = 'Прайс-листы'
