from django.conf.urls import url

from .views import RegisterView, LoginView, LogOutView, RegisterConfirmView, ResetPasswordConfirmView
from .views import ResetPasswordRequestView, RegisterRepeatView, ResetPasswordInplace

register = RegisterView.as_view()
register_confirm = RegisterConfirmView.as_view()
register_repeat = RegisterRepeatView.as_view()
login = LoginView.as_view()
logout = LogOutView.as_view()
password_request = ResetPasswordRequestView.as_view()
password_confirm = ResetPasswordConfirmView.as_view()
password_reset_inplace = ResetPasswordInplace.as_view()

urlpatterns = [
    url(r'^register/$', register, name='register'),
    url(r'^register_confirm/(?P<uidb64>[0-9A-Za-z]+)/$', register_confirm, name='register_confirm'),
    url(r'^register_repeat/$', register_repeat, name='register_repeat'),
    url(r'^login/$', login, name='login'),
    url(r'^logout/$', logout, name='logout'),
    url(r'^password_reset_request/$', password_request, name='password_request'),
    url(r'^password_reset_confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', password_confirm, name='password_confirm'),
    url(r'^password_reset_inplace/$', password_reset_inplace, name='password_reset_inplace')
]
