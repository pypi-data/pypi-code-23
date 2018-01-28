from django.urls import include, path

from . import views


urlpatterns = [
    path('<slug>/', include([
        path('', views.campaign, name='campaign'),
        path('pledge/', views.pledge, name='pledge'),
        path('remind/', views.reminder, name='remind'),
    ])),
]
