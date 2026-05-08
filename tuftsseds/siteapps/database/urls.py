from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.generic.base import TemplateView

from . import views

app_name = 'database'

urlpatterns = [
    # path('', views.EventsListView.as_view(), name="databases"),
]