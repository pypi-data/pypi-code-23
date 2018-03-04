from django.views.decorators.http import require_http_methods
from .decorators import allowed_methods, is_logged_in
from .request import APIMethods
from .restview import RestView
from .models.event_models import FirebaseEvents
from django.views.decorators.csrf import ensure_csrf_cookie
from .response_utils import ApiResponse


@require_http_methods(["GET"])
@ensure_csrf_cookie
def get_csrf_token(request):
    from django.middleware.csrf import get_token
    return ApiResponse.success(get_token(request))


@is_logged_in
@allowed_methods({APIMethods.POST, APIMethods.DELETE})
class FirebaseView(RestView):

    model = FirebaseEvents

    def pre_process(self, api_request):
        api_request.get_meta().set_required_fields("registration_token")

    def process(self):
        if self._request.get_method() == APIMethods.POST:
            return self.put_or_create()
        return super(FirebaseView, self).process()
