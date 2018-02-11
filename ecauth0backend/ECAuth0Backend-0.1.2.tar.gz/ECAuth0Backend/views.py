from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from ECAuth0Backend.settings import AUTH0_BACKEND_SUCCESS_REDIRECT, AUTH0_BACKEND_FAILURE_REDIRECT


def auth_callback(request):
    """
    View to process the authentication code.
    Redirects to / if already logged in.
    :param request:
    :return:
    """
    if not request.user.is_anonymous():
        return redirect(AUTH0_BACKEND_SUCCESS_REDIRECT)
    user = authenticate(**request.GET)
    if user and not user.is_anonymous():
        login(request, user)
        return redirect(request.GET.get('redirect_success', AUTH0_BACKEND_SUCCESS_REDIRECT))
    else:
        return redirect(request.GET.get('redirect_failed', AUTH0_BACKEND_FAILURE_REDIRECT))
