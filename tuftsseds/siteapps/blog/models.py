import os
from pathlib import Path
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from taggit.managers import TaggableManager

class Category(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = 'Categories'
        
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("main:search_category", args={self.slug})

class Author(models.Model):
    author_name = models.CharField(max_length=255)
    email = models.EmailField(_('email address'), null=True, blank=True)
    personal_website = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.author_name


class Blog(models.Model):
    title = models.CharField(max_length=255)
    blog_file = models.CharField(max_length=255, blank=True)
    cover_image = models.URLField(null=True, blank=True)
    short_description = models.TextField(null=True, blank=True, max_length=158)
    related_proj_team = models.CharField(max_length=255, null=True, blank=True)
    slug = models.SlugField(max_length=255, unique=True)
    tags = TaggableManager()
    
    category = models.ManyToManyField(Category)
    author = models.ForeignKey(Author, null=True, on_delete=models.CASCADE)
    publish_date = models.DateField(auto_now=False, auto_now_add=False)
    edit_date = models.DateField(auto_now=True)


    class Meta:
        verbose_name_plural = 'Blogs'


        
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("blog:get_blog", args={self.slug})
