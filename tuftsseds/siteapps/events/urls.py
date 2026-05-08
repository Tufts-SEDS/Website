from django.urls import path

from . import views

app_name = 'events'

urlpatterns = [
    path('', views.EventsListView.as_view(), name="events"),
    path('<slug:slug>', views.get_event, name="get_event"),
]