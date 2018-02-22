#import backends
#import interfaces
from .interfaces import TemplateLoaderFactory
from .requestcontext import RequestContext
from .views import direct_to_template
from .views.utils import get_template_loader

TemplateLoaderFactory = TemplateLoaderFactory

__all__ = ['interfaces', 'backends', 'TemplateLoaderFactory', 'RequestContext']
