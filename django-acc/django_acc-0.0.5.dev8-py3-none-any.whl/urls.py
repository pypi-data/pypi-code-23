from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views


urlpatterns = [
    path('users/', views.CreateUserView.as_view(), name='create-user'),
    path('users/<int:pk>',
         views.RetrieveUserView.as_view(),
         name='user-detail'),
    path('login/', views.login, name='login')
]

urlpatterns = format_suffix_patterns(urlpatterns)
