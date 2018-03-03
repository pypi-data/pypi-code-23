from tcell_agent.appsensor.django import django_meta
from tcell_agent.instrumentation.manager import InstrumentationManager


def instrument_csrf_view_middleware():
    from django.middleware.csrf import CsrfViewMiddleware

    def _tcell_reject(_tcell_original_reject, self, request, reason):
        meta = django_meta(request)
        meta.csrf_reason = reason

        return _tcell_original_reject(self, request, reason)

    InstrumentationManager.instrument(CsrfViewMiddleware, "_reject", _tcell_reject)
