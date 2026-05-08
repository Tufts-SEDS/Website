from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.BlogsListView.as_view(), name="blogs"),
    path('<slug:slug>', views.get_blog, name="get_blog"),
]