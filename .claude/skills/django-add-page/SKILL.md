---
name: django-add-page
description: Add, change, or remove a page on the Tufts SEDS site (view + URL + template + nav + sitemap). Use when asked to create a new page, add a link to the navbar, or take a page down.
---

# Adding or removing a page

Each page touches up to five places. Work through all of them. Missing one gives either a `NoReverseMatch` error or a dead link.

## 1. View (`tuftsseds/siteapps/<app>/views.py`)
Views are function-based and pass a `metacontent` dict, which the base templates put into `<meta>` tags for SEO:
```python
def my_page(request):
    metacontent = {
        "description": "One or two sentences for search engines.",
        "author": "",
        "keywords": "space, Tufts, SEDS, ...",
    }
    return render(request, "main/my-page.html", {"metacontent": metacontent})
```
To show events for a project team, filter by `related_proj_team` (`"rocketry"`, `"hab"`, `"cubesat"`, ...):
```python
Events.objects.filter(related_proj_team="cubesat").order_by("date")
```

## 2. URL (`tuftsseds/siteapps/<app>/urls.py`)
Each app sets `app_name`, so templates refer to URLs as `{% url 'main:my_page' %}`:
```python
path("my-page", views.my_page, name="my_page"),
```
A new app also needs a line in `tuftsseds/tuftsseds_core/urls.py` (see the `django-new-app` skill).

## 3. Template (`tuftsseds/templates/<app>/...`)
Extend a base template and fill the `content` block. Copy the structure from a similar existing page. There are several bases:
- `base.html`: the default site chrome
- `base_about_us.html`, `base_astrophotography.html`, `base_burner.html`: section-specific variants

## 4. Navigation: every base template has its own nav
The navbar and footer are copied into each base file, not shared. When you add or remove a nav link, update all of them:
```bash
grep -n "events:events" tuftsseds/templates/base*.html tuftsseds/templates/baser
```
Some bases also have a small `curr_page.includes("...")` script that highlights the active tab. Add or remove that branch too.

## 5. Sitemap (`tuftsseds/tuftsseds_core/sitemap.py`)
Add the URL name to `StaticViewSitemap.items()` for a public static page. For a model with detail pages, add a `Sitemap` class and register it in `tuftsseds_core/urls.py`.

## Removing a page
Do the steps above in reverse, then search the whole project for leftovers:
```bash
git grep -n -i "<name>" -- . ':!tuftsseds/static'
```
Look in the views, the templates (including search results and homepages), the sitemap, and `INSTALLED_APPS`. If the page had a model, follow the `django-models-migrations` skill to remove its data safely.

## Verify
Run `python manage.py check`, then load the new page and at least one page built on each base template you edited. See `django-local-dev`.
