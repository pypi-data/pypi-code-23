from django.shortcuts import redirect
from ohm2_handlers_light.decorators import ohm2_handlers_light_safe_request
from functools import wraps

def ohm2_accounts_light_safe_request(function):
	return ohm2_handlers_light_safe_request(function, "accounts")

def ohm2_accounts_light_redirect_if_authenticated(redirect_url = "/"):

	def decorator(view_function):
		@wraps(view_function)
		def wrapped_view(request, *args, **kwargs):
			if request.user.is_authenticated:
				return redirect(redirect_url)
			return view_function(request, *args, **kwargs)
		
		return wrapped_view
	
	return decorator