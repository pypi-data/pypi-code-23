import importlib
import sys, os
from django.views.decorators.csrf import csrf_protect
import json
from django.template.response import TemplateResponse
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.functional import SimpleLazyObject

from django.http import Http404
from django.http import HttpResponseRedirect

from . import models
import re

#add path for importation of plugins
sys.path.append(os.path.join(os.path.realpath(os.path.dirname(__file__)), '..'))



PAGE_PLUGINS = getattr(settings, 'PAGE_PLUGINS', ())

reg_v = re.compile(
    r"1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\\-(n|u)|c55\\/|capi|ccwa|cdm\\-|cell|chtm|cldc|cmd\\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\\-s|devi|dica|dmob|do(c|p)o|ds(12|\\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\\-|_)|g1 u|g560|gene|gf\\-5|g\\-mo|go(\\.w|od)|gr(ad|un)|haie|hcit|hd\\-(m|p|t)|hei\\-|hi(pt|ta)|hp( i|ip)|hs\\-c|ht(c(\\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\\-(20|go|ma)|i230|iac( |\\-|\\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\\/)|klon|kpt |kwc\\-|kyo(c|k)|le(no|xi)|lg( g|\\/(k|l|u)|50|54|e\\-|e\\/|\\-[a-w])|libw|lynx|m1\\-w|m3ga|m50\\/|ma(te|ui|xo)|mc(01|21|ca)|m\\-cr|me(di|rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\\-2|po(ck|rt|se)|prox|psio|pt\\-g|qa\\-a|qc(07|12|21|32|60|\\-[2-7]|i\\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\\-|oo|p\\-)|sdk\\/|se(c(\\-|0|1)|47|mc|nd|ri)|sgh\\-|shar|sie(\\-|m)|sk\\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\\-|v\\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\\-|tdg\\-|tel(i|m)|tim\\-|t\\-mo|to(pl|sh)|ts(70|m\\-|m3|m5)|tx\\-9|up(\\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|xda(\\-|2|g)|yas\\-|your|zeto|zte\\-",
    re.I | re.M)
re_comment = re.compile(r"<!--(.*?)-->")


class page_fallback_middleware(object):
    def process_request(self, request):
        request.page_site = models.get_page_site(request)
        if models.PAGE_USER == 'page.Page_User':
            #TODO fix this double lookup!
            request.page_user = SimpleLazyObject(lambda: models.Page_User.objects.get(pk=request.user.pk))
        else:
            request.page_user = SimpleLazyObject(
                lambda: models.get_page_site_user().objects.filter(user=request.user)[0])
        return None

    def process_response(self, request, response):
        request.page = None

        if response.status_code != 404:
            return response # No need to check for a flatpage for non-404 responses.
        try:
            return page_view(request)


        # Return the original response if any errors happened. Because this
        # is a middleware, we can't assume the errors will be caught elsewhere.
        except Http404:
            return response

#        except AttributeError:
#            return response
        except:
            if settings.DEBUG:
                raise
            return response

@csrf_protect
def page_view(request):
    context = {}

    page = models.get_page(request)


    if request.GET.get('history'):
        history = page.page_version_set.all()
        version_id = request.GET.get('version')
        if version_id:
            for version in history:
                if version.pk == int(version_id):
                    context['version'] = version
                    obj = json.loads(version.data)[0]['fields']
                    for k, v in obj.items():
                        excludes = ["post_ptr", 'site']
                        if not k in excludes:
                            setattr(page, k, v)
                    if request.GET.get('revert') and request.user.has_perm(models.get_class_model_perm(models.PAGE_PAGE, 'change')):
                        page.save()
                        history = None
                        break
        context['history'] = history

    if page and page.content:
        if page and page.members_only and not request.user.is_authenticated():
            return HttpResponseRedirect(reverse('login') + "?next=/" + page.slug)

        request.page = page
        #print "page banners = %s" % page.banners

        page.new_content = '' #recreate response, since wecan't modofy page.content and use search
        new_content_pos = 0

        #re
        if True:
            matches = re_comment.finditer(page.content)
            for match in matches:
                #import logging
                #logging.debug("match:%s" % match.group(0))
                comment = match.group(0)
                for plugin in PAGE_PLUGINS:
                    try:
                        mod = importlib.import_module(plugin)
                    except ImportError as e:
                        raise ImportError(
                            "Could not import settings '%s' (Is it on sys.path? Does it have syntax errors?)" % plugin)

                    response = mod.get(comment, request)
                    if response:
                        page.new_content += page.content[new_content_pos:match.start()] + response
                        new_content_pos = match.end()
            page.new_content += page.content[new_content_pos:]
            page.content = page.new_content
    context['slug'] = request.path[1:]
    context['object'] = page
    context['page'] = page
    context['user_page_add'] = request.user.has_perm(models.get_class_model_perm(models.PAGE_PAGE, 'add'))

    #print 'set context'
    if page:
        if request.user.has_perm(models.get_class_model_perm(models.PAGE_PAGE, 'change')):
            context['user_page_edit'] = True
        elif request.user.is_authenticated() and models.Page_Editor.objects.filter(editor=request.page_user,
                                                                                   page=page).count():
            context['user_page_edit'] = True
        else:
            context['user_page_edit'] = False

    template = 'page/page_detail.html'

    return TemplateResponse(
        request=request,
        template=template,
        context=context
    ).render()