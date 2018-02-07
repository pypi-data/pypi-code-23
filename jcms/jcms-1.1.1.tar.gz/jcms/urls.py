from django.urls import path
from jcms.models import Option, Article
from django.contrib.auth.models import User, Group
from jcms.mixins.jcms_crud import JcmsCrud

from jcms.helpers import functions
from .views import loginViews, groupsViews

app_name = 'jcms'

option_view = JcmsCrud(Option, ['type', 'value'])
articles_view = JcmsCrud(Article, ['code', 'title', 'content'], ['code', 'title'])
user_view = JcmsCrud(User, ['username', 'first_name', 'last_name', 'email', 'password', 'groups', 'is_staff',
                              'is_active', 'is_superuser'], ['username', 'email', 'groups', 'is_active'])
groups_view = JcmsCrud(Group, ['name', 'permissions'])

crud_models = [
    option_view,
    articles_view,
    user_view,
    groups_view
]

urlpatterns = [
    # login views
    path('', loginViews.LoginView.as_view(), name="login"),
    path('logout/', loginViews.logout_user, name="logoutUser"),
]

urlpatterns += functions.add_crud(crud_models)
urlpatterns += functions.add_menu_urls()
