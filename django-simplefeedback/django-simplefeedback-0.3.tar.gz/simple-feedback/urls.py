from django.conf.urls import url

from .views import TicketCreateAPIView


urlpatterns = [
    url(r"^tickets/$", view=TicketCreateAPIView.as_view(), name="ticket-create"),
]
