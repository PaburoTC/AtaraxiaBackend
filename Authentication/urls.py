from django.urls import path, re_path
from Authentication import views

urlpatterns = [
    path('register', views.register),
    path('login', views.login),
    path('set-csrf-cookie', views.set_csrf_token),
    path('googleLogin', views.google_login),
    re_path(r"user/([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", views.user_by_email),
    path('user/<uuid:uuid>', views.user_by_uuid),
    path('user/<str:username>', views.user_by_username)
]
