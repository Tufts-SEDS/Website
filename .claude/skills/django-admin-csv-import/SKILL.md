---
name: django-admin-csv-import
description: Add or change a spreadsheet CSV upload in the Django admin for Tufts SEDS models. Use when officers need to bulk-load or update data from the Google Drive "Master Lists", or when a CSV upload fails.
---

# Admin CSV uploads

Most site content (events, exec members, photos, rocketry data) comes from the "Master List" spreadsheets in the club Google Drive. An officer exports a sheet as CSV and uploads it through a custom admin page. Each spreadsheet column maps to a model field.

## How it works
- `ModelAdmin.get_urls()` adds an `upload-csv/` route in front of the default admin URLs.
- `upload_csv(request)` reads each file with pandas and calls `update_or_create`, keyed on a natural field (usually `title` or `name`). Re-uploading a sheet therefore updates existing rows instead of duplicating them.
- The upload form is `tuftsseds/templates/admin/csv_upload.html`.
- The "Upload a csv file" link on the model's list page comes from `tuftsseds/templates/admin/<app_label>/change_list.html`. That override applies to every model in the app.

For a full example, see `EventsAdmin` in `tuftsseds/siteapps/events/admin.py`.

## Adding an upload to a model
1. Copy the `get_urls` and `upload_csv` pattern from `EventsAdmin`.
2. Write down the exact column headers you rely on. The code indexes `row["..."]` by header name, so a renamed spreadsheet column causes a `KeyError`. Add a comment listing the expected headers.
3. Handle blank cells: pandas gives `NaN` for empty cells, and those are truthy. Use `pd.isna(row["col"])` before calling `.strip()` or `.split()`.
4. Parse dates explicitly, e.g. `datetime.strptime(row["date"], "%m/%d/%Y")`.
5. If the app has no `templates/admin/<app_label>/change_list.html` yet, add one so the upload link appears.

## Debugging a failed upload
- `KeyError: 'some column'`: the spreadsheet header doesn't match. Compare the headers against the code.
- `AttributeError: 'float' object has no attribute 'strip'`: an empty cell (NaN). Add a `pd.isna` guard.
- `IntegrityError` on a unique field (such as `Events.cover_image`): two rows share a value.
- Test with a small CSV on local SQLite before anyone uploads to production.
