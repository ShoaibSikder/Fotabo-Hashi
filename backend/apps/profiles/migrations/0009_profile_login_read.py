from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("profiles", "0008_remove_profile_profile_image"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                DROP POLICY profiles_profile_select ON profiles_profile;
                CREATE POLICY profiles_profile_select ON profiles_profile FOR SELECT USING (
                    (
                        current_setting('app.is_authenticated', true) = 'true' AND
                        (
                            current_setting('app.is_admin', true) = 'true' OR
                            user_id::text = current_setting('app.user_id', true)
                        )
                    ) OR (
                        current_setting('app.login_email', true) <> '' AND
                        user_id IN (
                            SELECT id FROM accounts_user
                            WHERE email = current_setting('app.login_email', true)
                        )
                    )
                );
            """,
            reverse_sql="""
                DROP POLICY profiles_profile_select ON profiles_profile;
                CREATE POLICY profiles_profile_select ON profiles_profile FOR SELECT USING (
                    current_setting('app.is_authenticated', true) = 'true' AND
                    (
                        current_setting('app.is_admin', true) = 'true' OR
                        user_id::text = current_setting('app.user_id', true)
                    )
                );
            """,
        ),
    ]
