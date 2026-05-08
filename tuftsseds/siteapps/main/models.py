from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from datetime import date


class CustomAccountManager(BaseUserManager):
    def create_superuser(self, email, name, password, **other_fields):
        other_fields.setdefault("is_staff", True)
        other_fields.setdefault("is_superuser", True)
        other_fields.setdefault("is_active", True)

        if other_fields.get("is_staff") is not True:
            raise ValueError("Superuser must be assigned to is_staff=True.")
        if other_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must be assigned to is_superuser=True.")

        return self.create_user(email, name, password, **other_fields)

    def create_user(self, email, name, password, **other_fields):
        if not email:
            raise ValueError(_("You must provide an email address"))

        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **other_fields)
        user.set_password(password)
        user.save()
        return user


class Chapters(models.Model):
    chapter_name = models.CharField(max_length=300)


class BaseSEDSMember(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("email address"), unique=True)
    name = models.CharField(max_length=150)  # Full, REAL name
    chapter_affiliation = models.ManyToManyField(Chapters)
    project_lead = models.BooleanField(default=False)

    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_blacklisted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = CustomAccountManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    class Meta:
        verbose_name = "Accounts"
        verbose_name_plural = "Accounts"

    def email_user(self, subject, message):
        send_mail(
            subject,
            message,
            "l@1.com",
            (self.email),
            fail_silently=False,
        )

    def __str__(self):
        return self.email


class ExecMembers(models.Model):
    # ORDER IN EACH OF THESE LISTS OF TUPLES MATTER, USED TO DECIDE
    # THE ORDER IN WHICH MEMBERS ARE DISPLAYED ON THE MEMBERS PAGE
    TEAM_LEAD_ROLES = (
        ("Rocketry Lead", "Rocketry Lead"),
        ("Weather Balloon Lead", "Weather Balloon Lead"),
        ("Astrophotography Lead", "Astrophotography Lead"),
        ("CubeSat Lead", "CubeSat Lead"),
        ("Radio Telescope Lead", "Radio Telescope Lead"),
        ("Mars Rover Lead", "Mars Rover Lead"),
    )
    YEAR = (
        ("2018-2019", "2018-2019"),
        ("2019-2020", "2019-2020"),
        ("2021-2022", "2021-2022"),
        ("2022-2023", "2022-2023"),
        ("2023-2024", "2023-2024"),
        ("2024-2025", "2024-2025"),
        ("2025-2026", "2025-2026"),
    )

    first_name = models.CharField(max_length=255, db_index=True)
    last_name = models.CharField(max_length=255, db_index=True)
    picture = models.CharField(max_length=255, db_index=True, null=True, blank=True)
    ordering = models.IntegerField(blank=True, null=True)
    active = models.BooleanField(default=False)

    # Social media links
    linkedin = models.URLField(blank=True, null=True)
    personal_site = models.URLField(blank=True, null=True)
    youtube = models.URLField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "SEDS Executive Members"

    def deactivate(self):
        last_year_active = self.active_years.partition("-")[2]
        today = date.today()
        final_day_active = date(int(last_year_active), 6, 30)
        if today >= final_day_active:
            self.active = False
        self.save()

    def __str__(self):
        return self.first_name + " " + self.last_name


class YearAndRole(models.Model):
    year = models.CharField(max_length=255, db_index=True)
    role = models.CharField(max_length=255, db_index=True)
    seds_member = models.ForeignKey(ExecMembers, null=True, on_delete=models.CASCADE)
    is_eboard = models.BooleanField(default=False)
    is_project_lead = models.BooleanField(default=False)

    def __str__(self):
        return self.year + ", " + self.role


class MailingList(models.Model):
    user_email = models.EmailField(_("email address"), unique=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user_email


##### Astrophotography Related Tables #####


class CameraData(models.Model):
    name = models.CharField(max_length=255)
    lens = models.CharField(max_length=255)
    # photo = models.ForeignKey(AstrophotographyPhotos, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class AstrophotographyPhotos(models.Model):
    name = models.CharField(max_length=255)
    photo = models.CharField(max_length=255, db_index=True, null=True, blank=True)
    caption = models.CharField(max_length=255, blank=True, null=True)
    target = models.CharField(max_length=255)

    # camera data
    camera_model = models.ForeignKey(CameraData, on_delete=models.CASCADE)

    # image data
    iso = models.CharField(max_length=64)
    focal_length = models.CharField(max_length=64)
    aperture = models.CharField(max_length=64)
    exposure_time = models.CharField(max_length=64, blank=True, null=True)
    location = models.CharField(max_length=255)
    tracker = models.CharField(max_length=255, blank=True, null=True)
    guiding = models.CharField(max_length=255, blank=True, null=True)
    date_taken = models.DateField(blank=True, null=True)
    photo_credit = models.CharField(max_length=255, blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    homepage_active = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Astrophotography Photos"
        verbose_name_plural = "Astrophotography Photos"

    def __str__(self):
        return self.name
