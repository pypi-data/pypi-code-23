from widget import ModelJobAPI

# we don't create a cached version of this because we really don't want to!
# jobs can be updated pretty low level....
from django_framework.django_helpers.api_helpers import get_api

def _get_proper_api_class(model_name_slug):

    try:
        APIClass = get_api(api_name = model_name_slug + '_job') # these must be registered with these names for us to find it!
    except AttributeError:
        APIClass = ModelJobAPI 
    
    return APIClass


def api_model_jobs(request, model_name_slug, model_pk = None, model_uuid = None, admin = False):
    APIJobClass = _get_proper_api_class(model_name_slug = model_name_slug)
    
    api = APIJobClass(request = request, admin = admin, model_name = model_name_slug, model_pk = model_pk, model_uuid = model_uuid, job_pk = None)
    api.run()
    response = api.format_data(api.data)
    return response


def api_model_job(request, model_name_slug, model_pk = None, model_uuid = None, job_uuid = None, admin = False):
    APIJobClass = _get_proper_api_class(model_name_slug = model_name_slug)
    
    api = APIJobClass(request = request, admin = admin, model_name = model_name_slug, model_pk = model_pk, model_uuid=model_uuid, job_pk= job_uuid)
    api.run()
    response = api.format_data(api.data)
    return response


# def api_admin_model_jobs(request, model_name_slug, model_pk = None, model_uuid = None, job_uuid = None, admin = True):
#     api = ModelJobAPI(admin=True, model_name = model_name_slug, model_pk = model_pk, model_uuid=model_uuid, request = request)
#     api.run()
#     response = api.format_data(api.data)
#     return response
# 
# 
# def api_admin_model_job(request, model_name_slug, model_pk = None, model_uuid = None, job_uuid = None, admin = True):
#     api = ModelJobAPI(admin = True, model_name = model_name_slug, request = request, model_pk = model_pk,model_uuid=model_uuid, job_pk= job_uuid)
#     api.run()
#     response = api.format_data(api.data)
#     return response