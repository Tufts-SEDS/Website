from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from tuftsseds.siteapps.events.models import Events


class EventsSitemap(Sitemap):
    def items(self):
        return Events.objects.all().order_by("-date")

    def lastmod(self, obj):
        # Event pages don't change after they're posted; the event date is the
        # closest thing to a real modification date.
        return obj.date


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
