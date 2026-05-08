from datetime import datetime
from django.contrib import admin, messages
from django import forms
from django.urls import path
from django.http.response import HttpResponseRedirect
from django.shortcuts import render

from .models import (
    ExecMembers,
    BaseSEDSMember,
    YearAndRole,
    AstrophotographyPhotos,
    CameraData,
    MailingList,
)

admin.site.register(BaseSEDSMember)


@admin.action(description="Deactivate members")
def deactivate_members(modeladmin, request, queryset):
    queryset.update(active=False)


@admin.action(description="Activate members")
def activate_members(modeladmin, request, queryset):
    queryset.update(active=True)


class CsvImportForm(forms.Form):
    csv_upload = forms.FileField(
        widget=forms.ClearableFileInput(attrs={"multiple": True})
    )


admin.site.register(CameraData)

admin.site.register(MailingList)


@admin.register(AstrophotographyPhotos)
class AstrophotographyPhotosAdmin(admin.ModelAdmin):
    search_fields = ["name", "created", "updated"]
    list_display = ["name", "created", "updated"]

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path("upload-csv/", self.upload_csv),
        ]
        return new_urls + urls

    def upload_csv(self, request):
        if request.method == "POST":
            import pandas as pd
            csv_files = request.FILES.getlist("csv_upload")

            for csv_file in csv_files:
                if not csv_file.name.endswith(".csv"):
                    messages.warning(request, "The wrong file type was uploaded")
                    return HttpResponseRedirect(request.path_info)

                csv_data = pd.read_csv(csv_file)
                csv_data = csv_data.fillna("")

                for index, row in csv_data.iterrows():

                    # Must be in the format of month/date/year
                    datetime_str = row["date_taken"]
                    datetime_object = datetime.strptime(datetime_str, "%m/%d/%Y")

                    model, _ = CameraData.objects.update_or_create(
                        name=str(row["camera_model_name"]),
                        lens=str(row["camera_model_lens"]),
                    )
                    new_photo, _ = AstrophotographyPhotos.objects.update_or_create(
                        photo=str(row["photo"]),
                        defaults={
                            "name": str(row["name"]),
                            "caption": str(row["caption"]),
                            "target": str(row["target"]),
                            "iso": str(row["iso"]),
                            "focal_length": str(row["focal_length"]),
                            "aperture": str(row["aperture"]),
                            "exposure_time": str(row["exposure_time"]),
                            "location": str(row["location"]),
                            "tracker": str(row["tracker"]),
                            "guiding": str(row["guiding"]),
                            "date_taken": datetime_object,
                            "homepage_active": bool(row["active"]),
                            "camera_model": model,
                            "photo_credit": str(row["photo_credit"]),
                        },
                    )

                    new_photo.save()

        form = CsvImportForm()
        data = {"form": form}
        return render(request, "admin/csv_upload.html", data)


@admin.register(YearAndRole)
class YearAndRoleAdmin(admin.ModelAdmin):
    search_fields = ["year", "role", "seds_member"]
    list_display = ["year", "role", "seds_member"]


@admin.register(ExecMembers)
class ExecMembersAdmin(admin.ModelAdmin):
    actions = [deactivate_members, activate_members]

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path("upload-csv/", self.upload_csv),
        ]
        return new_urls + urls

    def upload_csv(self, request):
        if request.method == "POST":
            import pandas as pd
            csv_files = request.FILES.getlist("csv_upload")

            for csv_file in csv_files:
                if not csv_file.name.endswith(".csv"):
                    messages.warning(request, "The wrong file type was uploaded")
                    return HttpResponseRedirect(request.path_info)

                csv_data = pd.read_csv(csv_file)
                csv_data = csv_data.fillna("")

                for index, row in csv_data.iterrows():
                    # creating the 2D array with the member's active year and their respective role
                    year_and_chapter = []
                    year_and_eboard = []

                    # no idea why pandas was buggin, now i have to do it the stupid way
                    eboard_years = str(row["year_and_eboard_role"])
                    chapter_years = str(row["year_and_chapter_role"])
                    first_name = str(row["first_name"]).strip()
                    last_name = str(row["last_name"]).strip()

                    # Creating a list of year and positions had to populate the db with
                    if eboard_years:
                        eboard_year_and_roles = eboard_years.split("|")
                        for year_and_role in eboard_year_and_roles:
                            parts = year_and_role.strip().split(", ")
                            if len(parts) == 2:
                                year_and_eboard.append(tuple(parts))

                    if chapter_years:
                        chapter_year_and_roles = chapter_years.split("|")
                        for year_and_role in chapter_year_and_roles:
                            parts = year_and_role.strip().split(", ")
                            if len(parts) == 2:
                                year_and_chapter.append(tuple(parts))

                    if row["ordering"]:
                        theexec, _ = ExecMembers.objects.update_or_create(
                            first_name=first_name,
                            last_name=last_name,
                            defaults={
                                "picture": row["picture"],
                                "linkedin": str(row["linkedin"]),
                                "personal_site": str(row["personal_site"]),
                                "youtube": str(row["yt"]),
                                "ordering": int(row["ordering"]),
                                "active": bool(row["active"]),
                            },
                        )
                    else:
                        theexec, _ = ExecMembers.objects.update_or_create(
                            first_name=first_name,
                            last_name=last_name,
                            defaults={
                                "picture": row["picture"],
                                "linkedin": str(row["linkedin"]),
                                "personal_site": str(row["personal_site"]),
                                "youtube": str(row["yt"]),
                                "active": bool(row["active"]),
                            },
                        )

                    theexec.save()

                    for item in year_and_eboard:
                        year_and_role, created = YearAndRole.objects.update_or_create(
                            year=item[0],
                            role=item[1],
                            seds_member=theexec,
                            defaults={"is_eboard": True, "is_project_lead": False},
                        )

                    for item in year_and_chapter:
                        year_and_role, created = YearAndRole.objects.update_or_create(
                            year=item[0],
                            role=item[1],
                            seds_member=theexec,
                            defaults={"is_eboard": False, "is_project_lead": True},
                        )

        form = CsvImportForm()
        data = {"form": form}
        return render(request, "admin/csv_upload.html", data)
