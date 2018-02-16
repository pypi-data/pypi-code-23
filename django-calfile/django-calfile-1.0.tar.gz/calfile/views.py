from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .utils import get_cal_serialize_file

@csrf_exempt
@require_http_methods(["POST"])
def calfile(request):
    start_date = request.POST.get("start_date", "")
    end_date = request.POST.get("end_date", "") 
    summary = request.POST.get("summary", "Summary")
    filename = request.POST.get("filename", "calfile")

    icalstream = get_cal_serialize_file(start_date, end_date, summary)
    
    response = HttpResponse(icalstream)
    response['Content-Disposition'] = f"attachment; filename={filename}.ics"
    return response
