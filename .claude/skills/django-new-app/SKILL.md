---
name: django-new-app
description: Create a new Django app under tuftsseds/siteapps and wire it into settings, URLs, admin, and templates. Use when a feature needs its own models (a new project team database, a new content type), not just a new page.
---

# Creating a new app

Only create an app when the feature has its own models. For a new page, use the `django-add-page` skill.

## Steps
1. Generate the app inside `siteapps` and run the command from the repo root:
   ```bash
   mkdir tuftsseds/siteapps/<app>
   python manage.py startapp <app> tuftsseds/siteapps/<app>
   ```
2. Fix `apps.py`. The name must be the full dotted path:
   ```python
   class <App>Config(AppConfig):
       default_auto_field = "django.db.models.BigAutoField"
       name = "tuftsseds.siteapps.<app>"
   ```
3. Register the app in `INSTALLED_APPS` in `tuftsseds/tuftsseds_core/settings.py`:
   `"tuftsseds.siteapps.<app>.apps.<App>Config",`
4. URLs: create `urls.py` with `app_name = "<app>"`, then include it from `tuftsseds/tuftsseds_core/urls.py`:
   `path("<app>/", include("tuftsseds.siteapps.<app>.urls")),`
5. Put templates in `tuftsseds/templates/<app>/`, not inside the app folder.
6. Admin: register the models. If officers will load the data from a spreadsheet, add a CSV upload (see `django-admin-csv-import`).
7. Create the first migration with `python manage.py makemigrations <app>`, and commit the migration file with the model.

## Cross-app references
Import models by their full path, e.g. `from tuftsseds.siteapps.events.models import Events`.

Think twice before adding a foreign key to a model in another app. It makes that app impossible to delete cleanly later. When the blog app was removed, `Events.author` pointed at `blog.Author` and needed a migration-history rewrite (see `events/migrations/0003` and `0008`). If two apps share a model, put it in the app that will outlive the other.

## Verify
Run `python manage.py check` and `python manage.py makemigrations --check`, then load the app's pages and admin list.
