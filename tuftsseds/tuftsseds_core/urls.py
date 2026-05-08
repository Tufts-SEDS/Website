"""tuftsseds URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from .sitemap import EventsSitemap, BlogsSitemap, StaticViewSitemap
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("tuftsseds.siteapps.main.urls")),
    path(
        "sitemap.xml",
        sitemap,
        {
            "sitemaps": {
                "static": StaticViewSitemap,
                "events": EventsSitemap,
                "blogs": BlogsSitemap,
            }
        },
    ),
    path("blog/", include("tuftsseds.siteapps.blog.urls")),
    path("events/", include("tuftsseds.siteapps.events.urls")),
    path("database/", include("tuftsseds.siteapps.database.urls")),
    path("account/", include("tuftsseds.siteapps.account.urls")),
    path("account/", include("django.contrib.auth.urls")),
    # path("__debug__/", include("debug_toolbar.urls")),
]
