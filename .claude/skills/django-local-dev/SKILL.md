---
name: django-local-dev
description: Set up, run, and verify the Tufts SEDS Django site locally. Use when someone asks how to run the site, gets an environment or database connection error, or needs to confirm a change works before committing.
---

# Running the Tufts SEDS site locally

## Layout
- `manage.py` sits at the repo root. Run every Django command from there.
- Settings live in `tuftsseds/tuftsseds_core/settings.py`. `DJANGO_SETTINGS_MODULE` is `tuftsseds.tuftsseds_core.settings`.
- Apps live in `tuftsseds/siteapps/<app>/` (`main`, `events`, `database`, `account`).
- Templates are in `tuftsseds/templates/`, one folder per app. Static files are in `tuftsseds/static/`.

## Environment
1. Create a Python environment: either `conda env create -f sedsite.yml -n sedsite`, or `python -m venv .venv` followed by `pip install -r requirements.txt`. Vercel installs from `requirements.txt`, so treat that file as the source of truth for dependencies.
2. Create a `.env` file at the repo root. It is gitignored, so never commit it. It needs these keys:
   - `DEBUG`: `True` locally. Never set it to `False` unless you mean to use production settings.
   - `REGULAR_DB`: `True` uses a local SQLite file (`tuftsseds/db.sqlite3`). `False` uses the Postgres database described by the `PG*` variables.
   - `SECRET_KEY`
   - `PGDATABASE`, `PGUSER`, `PGPASSWORD`, `PGHOST`, `PGPORT`: ask a club officer for these. Don't paste them into chat, issues, or commits.
3. Start the server with `python manage.py runserver`, then open http://127.0.0.1:8000.

## Which database am I using?
- `DEBUG=True` + `REGULAR_DB=True`: local SQLite. Safe to break.
- `REGULAR_DB=False`: the shared Postgres database named in `.env`. Anything you write there is real, so confirm which database the `PG*` variables point to before you run `migrate` or edit data.

## Known SQLite limitation
`main/migrations/0007_*` uses Postgres `ArrayField`, so `migrate` on a fresh SQLite database stops there. For local work that doesn't touch `main`:
```bash
python manage.py migrate main 0006
python manage.py migrate main 0007 --fake   # Pages that use exec members won't work
python manage.py migrate
```
To test a whole page flow end to end, use the Postgres test database instead.

## Verify a change before committing
There are no automated tests yet. At a minimum, run:
```bash
python manage.py check
python manage.py makemigrations --check --dry-run   # Fails if a model changed without a migration
```
Then load every page you touched. For a quick scripted smoke test:
```bash
python manage.py shell -c "
from django.conf import settings; settings.ALLOWED_HOSTS.append('testserver')
from django.test import Client
c = Client()
for url in ['/', '/events/', '/sitemap.xml']:
    print(url, c.get(url).status_code)
"
```
A 500 prints its traceback, so read it rather than assuming a page works.

Note: `makemigrations --check` currently reports pending changes in the `database` app. That predates this skill, so don't "fix" it in an unrelated PR.
