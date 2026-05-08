from django.contrib import admin
from datetime import datetime
from django.contrib import admin, messages
from django import forms
from django.urls import path
from django.http.response import HttpResponseRedirect
from django.utils.text import slugify
from django.shortcuts import render

import pandas as pd

from .models import Events
from tuftsseds.siteapps.blog.models import Author


class CsvImportForm(forms.Form):
    csv_upload = forms.FileField(
        widget=forms.ClearableFileInput(attrs={"multiple": True})
    )


@admin.register(Events)
class EventsAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path("upload-csv/", self.upload_csv),
        ]
        return new_urls + urls

    def upload_csv(self, request):
        if request.method == "POST":
            csv_files = request.FILES.getlist("csv_upload")

            for csv_file in csv_files:
                if not csv_file.name.endswith(".csv"):
                    messages.warning(request, "The wrong file type was uploaded")
                    return HttpResponseRedirect(request.path_info)

                csv_data = pd.read_csv(csv_file)

                for index, row in csv_data.iterrows():
                    # prepping tags field as a list
                    tag_list = row["tags"].split(",")

                    # Must be in the format of month/date/year
                    datetime_str = row["date"]
                    datetime_object = datetime.strptime(datetime_str, "%m/%d/%Y")

                    # Getting the project team the event is related to so it
                    # can be displayed on their homepage
                    if pd.isna(row["project team"]):
                        project_team = ""
                    else:
                        project_team = row["project team"].strip()

                    # Checking if the description in the csv is simply text or if
                    # it is written in HTML. This allows us to render the HTML
                    # rather than inserting it as text on the event page
                    if row["Using HTML for Description?"].lower() == "yes":
                        is_using_html = True
                    else:
                        is_using_html = False

                    # Creating/updating the actual event. using the title to query the db
                    # and see if it already exists. If it doesnt, we create a new event using
                    # all the attributes of an Events instance
                    the_event, created = Events.objects.update_or_create(
                        title=row["title"],
                        defaults={
                            "is_description_html": is_using_html,
                            "description": row["description"],
                            "cover_image": (row["cover image"]).strip(),
                            "folder_name": (row["folder_name"]).strip(),
                            "image_prepend_name": (row["image_prepend_name"]).strip(),
                            "photo_credits": (row["photo_cred"]).strip(),
                            "total_images": int(row["image_count"]),
                            "related_proj_team": project_team,
                            "date": datetime_object,
                            "slug": slugify(row["title"]),
                        },
                    )

                    # Adding the author to the event using the same logic from the code above
                    the_event.author, _ = Author.objects.get_or_create(
                        author_name=row["Author"]
                    )
                    the_event.save()

                    for tag in tag_list:
                        the_event.tags.add(tag)

        form = CsvImportForm()
        data = {"form": form}
        return render(request, "admin/csv_upload.html", data)
