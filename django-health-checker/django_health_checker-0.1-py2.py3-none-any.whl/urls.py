from health_checker import views
from django.urls import path

urlpatterns = [
    path('', views.HealthCheckCustomView.as_view(), name='health_check_custom'),
]