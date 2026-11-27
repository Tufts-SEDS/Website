from django.db import models
from django.templatetags.static import static
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager

from .images import cover_stem, thumb_name

# Shown instead of a cover photo when an event has none
FALLBACK_COVER = "images/logo.png"


class Author(models.Model):
    author_name = models.CharField(max_length=255)
    email = models.EmailField(_("email address"), null=True, blank=True)
    personal_website = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.author_name


class Events(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, null=True, on_delete=models.CASCADE)
    cover_image = models.URLField(max_length=500, blank=True, unique=True)
    date = models.DateField(auto_now=False, auto_now_add=False)
    description = models.TextField(blank=True, null=True)
    is_description_html = models.BooleanField(default=False)

    related_proj_team = models.CharField(max_length=255, null=True, blank=True)
    slug = models.SlugField(max_length=255, unique=True)
    tags = TaggableManager()

    folder_name = models.CharField(max_length=255, null=True, blank=True)
    image_prepend_name = models.CharField(max_length=255, null=True, blank=True)
    photo_credits = models.CharField(max_length=255, null=True, blank=True)
    total_images = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Events"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("events:get_event", args={self.slug})

    def _cover_static_path(self, thumb=False):
        stem = cover_stem(self.cover_image)
        if not stem or not self.folder_name:
            return FALLBACK_COVER
        name = thumb_name(stem) if thumb else f"{stem}.webp"
        return f"images/events/{self.folder_name}/{name}"

    @property
    def cover_url(self):
        """Full-size cover photo, or the site logo if the event has none."""
        return static(self._cover_static_path())

    @property
    def cover_thumb_url(self):
        """Small cover photo for cards and lists (made by `manage.py make_cover_thumbs`)."""
        return static(self._cover_static_path(thumb=True))
