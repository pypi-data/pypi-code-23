from django.apps import apps as django_apps
from django.shortcuts import render
from ohm2_handlers_light.decorators import ohm2_handlers_light_safe_request
from ohm2_handlers_light import utils as h_utils
from functools import wraps
from . import definitions
from . import settings


def ohm2_permissions_light_safe_request(function):
	return ohm2_handlers_light_safe_request(function, "ohm2_permissions_light")



def ohm2_permissions_light_has_permission(model_name, permission_query, db_query_function, **options):
	try:
		model = django_apps.get_model(model_name)
	except LookupError:
		raise definitions.ModelNotFound()
	
	allowed = False
	obj = query = db_query_function(model, **permission_query)
	if hasattr(query, "exist"):
		allowed = query.exist()
	elif hasattr(query, "count"):
		allowed = True if query.count() > 0 else False
	elif obj:
		allowed = True
	return (allowed, obj, model)

def ohm2_permissions_light_permission_required_or_render_template(model_name,
																  permission_query,
																  on_permission_not_found_template,
																  has_permission_function = ohm2_permissions_light_has_permission,
																  db_query_function = h_utils.db_get_or_none):

	def decorator(view_function):

		@wraps(view_function)
		def wrapped_view(request, *args, **kwargs):

			allowed, obj, model = has_permission_function(model_name, permission_query, db_query_function)
			if allowed:
				return view_function(request, *args, **kwargs)

			error = {
				"request": request,
			}
			return render(request, on_permission_not_found_template, {"error": error})

		return wrapped_view
	
	return decorator


