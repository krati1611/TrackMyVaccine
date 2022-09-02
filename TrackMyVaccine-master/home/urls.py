from django.urls import path, re_path
from . import views


urlpatterns = [
    re_path(r'^session', views.session_fetcher),
    path('', views.home),
]
