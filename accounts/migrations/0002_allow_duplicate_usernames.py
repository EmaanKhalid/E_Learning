from django.db import migrations


def remove_username_unique_constraint(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("""
            ALTER TABLE auth_user
            DROP CONSTRAINT IF EXISTS auth_user_username_key;
        """)


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            remove_username_unique_constraint,
            migrations.RunPython.noop,
        ),
    ]