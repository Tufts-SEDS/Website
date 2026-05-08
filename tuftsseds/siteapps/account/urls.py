from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "account"

urlpatterns = [
    path("login-register/", views.login_register, name="login_register"),
    path("activate/<slug:uidb64>/<slug:token>/", views.activate, name="activate"),
    path("reset-password/", views.account_register, name="reset_password"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path(
        "dashboard/event-image-manager",
        views.event_image_manager,
        name="event_image_manager",
    ),
    path(
        "dashboard/event-image-manager/<slug:slug>", views.edit_event, name="edit_event"
    ),
    # path('dashboard/upload-rocket-model', views.rocketmodel_upload, name='upload_rocket'),
]
