from datetime import datetime
from django.contrib import admin, messages
from django import forms
from django.urls import path
from django.http.response import HttpResponseRedirect
from django.utils.text import slugify
from django.shortcuts import render

from .models import Author, Blog, Category

class CsvImportForm(forms.Form):
    csv_upload = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [path('upload-csv/', self.upload_csv),]
        return new_urls + urls

    def upload_csv(self, request):

        if request.method == "POST":
            import pandas as pd
            csv_files = request.FILES.getlist('csv_upload')

            for csv_file in csv_files:
                if not csv_file.name.endswith('.csv'):
                    messages.warning(request, 'The wrong file type was uploaded')
                    return HttpResponseRedirect(request.path_info)
                

                csv_data = pd.read_csv(csv_file)

                for index, row in csv_data.iterrows():

                    # prepping category field as a list
                    category_list = row["categories"].split(',')

                    # prepping tags field as a list
                    tag_list = row["tags"].split(',')

                    # Must be in the format of month/date/year
                    datetime_str = row["publish date"]
                    datetime_object = datetime.strptime(datetime_str, '%m/%d/%Y')
                    
                    # Getting the project team the blog is related to so it
                    # can be displayed on their homepage
                    if pd.isna(row["project team"]):
                        project_team = ""
                    else:
                        project_team = row["project team"].strip()


                    theblog, _ = Blog.objects.update_or_create(
                        title = row["title"],
                        defaults = {
                            'short_description' : row["short description"],
                            'blog_file' : row["blog file"],
                            'cover_image' : row["cover image"],
                            'related_proj_team': project_team,
                            'publish_date' : datetime_object,
                            'slug' : slugify(row["title"])
                        }
                    )

                    theblog.author, _ = Author.objects.get_or_create(author_name = row["author"])
                    theblog.save()

                    for category_name in category_list:
                        category, created = Category.objects.update_or_create(
                            slug = slugify(category_name),
                            defaults={'name': category_name})
                        theblog.category.add(category)

                    for tag in tag_list:
                        theblog.tags.add(tag)


        form = CsvImportForm()
        data = {"form": form}
        return render(request, "admin/csv_upload.html", data)

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [path('upload-csv/', self.upload_csv),]
        return new_urls + urls

    def upload_csv(self, request):

        if request.method == "POST":
            import pandas as pd
            csv_files = request.FILES.getlist('csv_upload')

            for csv_file in csv_files:
                if not csv_file.name.endswith('.csv'):
                    messages.warning(request, 'The wrong file type was uploaded')
                    return HttpResponseRedirect(request.path_info)
                

                csv_data = pd.read_csv(csv_file)

                for index, row in csv_data.iterrows():
                
                    the_author, _ = Author.objects.update_or_create(
                        author_name = row["name"],
                        defaults = {
                            'email' : row["email"],
                            'personal_website' : row["site"],
                        }
                    )

        form = CsvImportForm()
        data = {"form": form}
        return render(request, "admin/csv_upload.html", data)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}