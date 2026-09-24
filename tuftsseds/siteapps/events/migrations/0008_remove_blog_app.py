# Removes the blog app: renames the Author table it left behind and deletes
# the remaining blog data (posts, categories, tags on posts, content types,
# permissions and migration history).

from django.db import migrations

BLOG_TABLES = ["blog_blog_category", "blog_blog", "blog_category"]


def delete_blog_data(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    TaggedItem = apps.get_model("taggit", "TaggedItem")

    # Keep the Author content type (and its permissions/admin history) by
    # moving it to events. Skip this if events.author already has one.
    if not ContentType.objects.filter(app_label="events", model="author").exists():
        ContentType.objects.filter(app_label="blog", model="author").update(
            app_label="events"
        )

    blog_types = ContentType.objects.filter(app_label="blog")
    TaggedItem.objects.filter(content_type__in=blog_types).delete()
    # Deletes the related permissions and admin log entries too
    blog_types.delete()

    existing_tables = schema_editor.connection.introspection.table_names()
    for table in BLOG_TABLES:
        if table in existing_tables:
            schema_editor.execute("DROP TABLE %s" % schema_editor.quote_name(table))

    schema_editor.execute("DELETE FROM django_migrations WHERE app = 'blog'")


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0007_delete_eventimage"),
        ("admin", "0003_logentry_add_action_flag_choices"),
        ("auth", "0012_alter_user_first_name_max_length"),
        ("contenttypes", "0002_remove_content_type_name"),
        ("taggit", "0005_auto_20220424_2025"),
    ]

    operations = [
        migrations.AlterModelTable(
            name="author",
            table=None,
        ),
        migrations.RunPython(delete_blog_data, migrations.RunPython.noop),
    ]
