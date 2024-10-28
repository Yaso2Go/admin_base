from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'admin_base'

urlpatterns = [

    path("admin/login/", auth_views.LoginView.as_view(template_name="login.html")),

    path("admin/logout/", auth_views.LogoutView.as_view(), name="logout"),
]