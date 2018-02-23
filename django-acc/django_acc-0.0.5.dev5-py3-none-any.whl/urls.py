from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

app_name = 'accounts'

urlpatterns = [
    path('users/', views.UserCreate.as_view(), name='create-user'),
    path('login/', views.login, name='login')
]

urlpatterns = format_suffix_patterns(urlpatterns)
