from datetime import datetime

from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from tuftsseds.siteapps.events.models import Events
from tuftsseds.siteapps.blog.models import Blog


class EventsSitemap(Sitemap):
    def items(self):
        return Events.objects.all().order_by("-date")

    def lastmod(self, obj):
        return datetime.now()


class BlogsSitemap(Sitemap):
    def items(self):
        return Blog.objects.all().order_by("-publish_date")

    def lastmod(self, obj):
        return obj.edit_date


class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = "daily"

    def items(self):
        return [
            "main:home",
            "main:rocket_hp",
            "main:weatherball_hp",
            "main:cubesat_hp",
            "main:astrophotography_hp",
            "main:leadership",
            "main:about_us",
            "events:events",
            "blog:blogs",
        ]

    def location(self, item):
        return reverse(item)
