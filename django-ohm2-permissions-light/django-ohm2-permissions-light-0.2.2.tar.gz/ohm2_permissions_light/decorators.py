from django.apps import apps as django_apps
from django.shortcuts import render
from ohm2_handlers_light.decorators import ohm2_handlers_light_safe_request
from ohm2_handlers_light import utils as h_utils
from functools import wraps
from . import definitions
from . import settings


def ohm2_permissions_light_safe_request(function):
	return ohm2_handlers_light_safe_request(function, "ohm2_permissions_light")



def ohm2_permissions_light_has_permission_adding_username(request, model_name, username_added_as = "user__username", **permission_kwargs):
	
	try:
		model = django_apps.get_model(model_name)
	except LookupError:
		raise definitions.ModelNotFound()
	
	permission_kwargs[username_added_as] = request.user.get_username()

	allowed = False
	obj = query = h_utils.db_get_or_none(model, **permission_kwargs)
	if hasattr(query, "exist"):
		allowed = query.exist()
	elif hasattr(query, "count"):
		allowed = True if query.count() > 0 else False
	elif obj:
		allowed = True
	return allowed

def ohm2_permissions_light_permission_required_or_render_template(on_permission_not_found_template,
	                                                              has_permission_function = ohm2_permissions_light_has_permission_adding_username,
																  permission_args = (),
																  permission_kwargs = {}):

	def decorator(view_function):

		@wraps(view_function)
		def wrapped_view(request, *args, **kwargs):

			allowed = has_permission_function(request, *permission_args, **permission_kwargs)
			if allowed:
				return view_function(request, *args, **kwargs)

			error = {
				"request": request,
			}
			return render(request, on_permission_not_found_template, {"error": error}, status = 403)

		return wrapped_view
	
	return decorator


