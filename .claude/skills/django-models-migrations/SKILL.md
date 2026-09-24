---
name: django-models-migrations
description: Safely change Django models and migrations for the Tufts SEDS site, including removing models or whole apps and applying migrations to production. Use whenever models.py changes, a migration is created or edited, or someone asks to run migrate against a real database.
---

# Models and migrations

The production database holds real club data (exec members, events, photos), and there are no automatic backups you should count on. Treat every migration as something that will run against it.

## Everyday workflow
1. Edit `models.py`.
2. Run `python manage.py makemigrations <app>` and read the generated file. Check that it is doing what you expect. For example, a `RemoveField` + `AddField` pair where you meant a rename will throw away that column's data. Use `RenameField`, or answer "yes" when Django asks whether you renamed a field.
3. Apply it locally with `python manage.py migrate` on SQLite (see `django-local-dev`).
4. Commit the model change and its migration together.

## Rules
- Don't edit or delete a migration that production has already applied. It's usually fine to add a new migration on top. The exception is when an app is being removed and older migrations depend on it, like `events/0003`. In that case, only edit history so that Django's recorded state still matches the real database schema, and explain why in a comment at the top of the file.
- Put data changes in a `RunPython` migration. Use `apps.get_model(...)`, never a direct import of the model.
- Keep nullable-to-required changes safe: add the field with `null=True`, backfill it, then make it required in a second migration.
- Postgres-only fields (`ArrayField`) break SQLite. If you add one, note it in `django-local-dev`.

## Removing a model or app
1. Delete the code that uses it (views, templates, admin, sitemap, search), then remove the models.
2. If other apps have foreign keys to it, move the shared model to the surviving app first and keep its data.
3. When removing a whole app, also clean up the data Django can't see anymore: its tables, `taggit` `TaggedItem` rows, `ContentType`s (which cascade to permissions and admin log entries), and its `django_migrations` rows. `events/migrations/0008_remove_blog_app.py` is a worked example.
4. Test the upgrade path, not only a fresh database. Copy a database that has the old schema and some sample rows, run the new migrations on it, and check the data survived.

## Applying migrations to production
Vercel deploys code but does not run `migrate`. After a PR with migrations is merged and deployed, someone with production credentials must run:
```bash
python manage.py showmigrations      # Check what's pending first
python manage.py migrate
```
Point the `PG*` variables in `.env` at the production database only for this step, then switch them back. Between the deploy and the migrate, the code and the schema don't match, so run the two back to back. Always tell the user when a change needs this step.
