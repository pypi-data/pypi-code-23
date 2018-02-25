from .definitions import RequestException
from django.shortcuts import redirect
from functools import wraps
import inspect
from . import settings


if settings.BYPASS_SAFE_REQUEST_DECORATOR:
	def ohm2_handlers_light_safe_request(func, app):

		@wraps(func)
		def wrapper(*args, **kwargs):
			return (func(*args, **kwargs), None)
		return wrapper

else:
	def ohm2_handlers_light_safe_request(func, app):

		@wraps(func)
		def wrapper(*args, **kwargs):
			try:
				result = func(*args, **kwargs)
			except Exception as original:
				tr = inspect.trace()[-1]
				
				exc = RequestException(app,
									   getattr(original, "code", None),
									   getattr(original, "message", None),
									   original,
									   ins_filename = tr.filename,
									   ins_lineno = tr.lineno,
									   ins_function = tr.function,
									   ins_code_context = tr.code_context)

				return (None, exc)
			
			else:
				return (result, None)

		return wrapper




def redirect_if_authenticated(view_function, redirect_url = "/"):

	@wraps(view_function)
	def wrapped_view(request, *args, **kwargs):
		if request.user.is_authenticated:
			return redirect(redirect_url)
		return view_function(request, *args, **kwargs)
	
	return wrapped_view