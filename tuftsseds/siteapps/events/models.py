from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager


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
