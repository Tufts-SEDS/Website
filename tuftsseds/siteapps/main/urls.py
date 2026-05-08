from django.urls import path
from django.views.generic.base import TemplateView

from . import views

app_name = "main"

urlpatterns = [
    # Main homepage links
    #############################
    path("", views.index, name="home"),
    path("leadership", views.leadership, name="leadership"),
    path("media", views.media, name="media"),
    path("about-us", views.about_us, name="about_us"),
    path("support-us", views.support_us, name="support_us"),
    path("burner", views.burner, name="burner"),  # delete when done
    # Project team specific pages
    #############################
    path("rocketry", views.rocket_hp, name="rocket_hp"),
    path("rocketry/sponsors", views.rocket_our_sponsers, name="rocket_our_sponsers"),
    path(
        "rocketry-become-a-sponsor",
        views.rocket_become_sponser,
        name="rocket_become_sponser",
    ),
    path("rocketry/donate", views.rocket_donate, name="rocket_donate"),
    path("rocketry/launches", views.rocket_launch, name="rocket_launch"),
    path("rocketry/leadership", views.rocket_leadership, name="rocket_leadership"),
    path("rocketry/projects", views.rocket_projects, name="rocket_projects"),
    # path("rocketry-gallery", views.rocket_gallery, name="rocket_gallery"),
    path("weather-balloon", views.weatherball_hp, name="weatherball_hp"),
    path("astrophotography", views.astrophotography_hp, name="astrophotography_hp"),
    path(
        "astrophotography_help",
        views.astrophotography_helper,
        name="astrophotography_helper",
    ),
    path("radio-telescope", views.radio_telescope_hp, name="radio_telescope_hp"),
    path("radio-telescope/news", views.radio_telescope_news, name="radio_telescope_news"),
    path("cubesat", views.cubesat_hp, name="cubesat_hp"),
    # Ajax forms
    #############################
    path("newsletter-signup", views.newsletter_signup, name="newsletter_signup"),
    path("get-image-info/", views.image_info, name="image_info"), # this is what gets the image info that astrophotography_helper displays in the modal
    # Search bar function
    #############################
    path("search-results", views.search, name="search"),
    path(
        "search-results/category=<slug:category_slug>",
        views.search_category,
        name="search_category",
    ),
    # Other/Misc.
    #############################
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),
]
