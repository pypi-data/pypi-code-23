from django.shortcuts import render

# Create your views here.

from django.http import JsonResponse
from crdist.models import Canton, District
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.forms.utils import flatatt
from crdist.utils import str_2_obj


def render_option(option_list, name, label=" ", function_load="",
                  prefix="", initial=0, attrs=None):

    attrs = flatatt(attrs) if attrs is not None else ""
    options = []
    for option in option_list:
        options.append('<option value="%d" %s >%s</option>' % (option.pk, 'selected="selected"' if initial == option.pk else "", option.name))

    label = '<label for="%s">%s: </label>' % ('id_' + prefix + name, label)
    if options:
        return mark_safe(label + """ <select %s id="%s" name="%s" onchange="%s">
        <option value="-1"> --- </option> %s 
        </select>""" % (attrs , 'id_' + prefix + name, prefix + name, function_load, " ".join(options)))

    return str(_("Not available"))


def get_canton(request):
    name = request.GET.get('name', '')
    canton = Canton.objects.filter(province__pk=request.GET.get('province', "0"))
    initial = request.GET.get("initial", "0")
    attrs = str_2_obj(request.GET.get('attrs', ''))

    try:
        initial = int(initial)
    except:
        initial = 0
    return JsonResponse({'id':'div_canton_' + name,
                         'content': render_option(canton, name,
                                                  label=_("Canton"),
                                                  function_load="load_district(this, undefined)",
                                                  prefix="canton_",
                                                  initial=initial,
                                                  attrs=attrs)})


def get_distric(request):
    name = request.GET.get('name', '')
    dists = District.objects.filter(canton__pk=request.GET.get('canton', "0"))
    initial = request.GET.get("initial", "0")
    attrs = str_2_obj(request.GET.get('attrs', ''))
    try:
        initial = int(initial)
    except:
        initial = 0
    return JsonResponse({'id':'div_district_' + name,
                         'content': render_option(dists, name,
                                                  label=_("District"),
                                                  function_load=" ",
                                                  prefix="",
                                                  initial=initial,
                                                  attrs=attrs)})


