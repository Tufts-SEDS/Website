from datetime import datetime

from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from tuftsseds.siteapps.events.models import Events


class EventsSitemap(Sitemap):
    def items(self):
        return Events.objects.all().order_by("-date")

    def lastmod(self, obj):
        return datetime.now()


class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = "daily"

    def items(self):
        return [
            "main:home",
            "main:rocket_hp",
            "main:cubesat_hp",
            "main:astrophotography_hp",
            "main:leadership",
            "main:about_us",
            "events:events",
            "events:calendar",
        ]

    def location(self, item):
        return reverse(item)
