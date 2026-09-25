from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("accounts", "0002_enable_rls")]

    operations = [
        migrations.RunSQL(
            """
            DROP POLICY accounts_user_update ON accounts_user;
            CREATE POLICY accounts_user_update ON accounts_user FOR UPDATE USING (
                (current_setting('app.is_authenticated', true) = 'true' AND
                 (current_setting('app.is_admin', true) = 'true' OR
                  id::text = current_setting('app.user_id', true))) OR
                email = current_setting('app.login_email', true)
            ) WITH CHECK (
                (current_setting('app.is_authenticated', true) = 'true' AND
                 (current_setting('app.is_admin', true) = 'true' OR
                  id::text = current_setting('app.user_id', true))) OR
                email = current_setting('app.login_email', true)
            );
            """,
            """
            DROP POLICY accounts_user_update ON accounts_user;
            CREATE POLICY accounts_user_update ON accounts_user FOR UPDATE USING (
                current_setting('app.is_authenticated', true) = 'true' AND
                (current_setting('app.is_admin', true) = 'true' OR
                 id::text = current_setting('app.user_id', true))
            ) WITH CHECK (
                current_setting('app.is_authenticated', true) = 'true' AND
                (current_setting('app.is_admin', true) = 'true' OR
                 id::text = current_setting('app.user_id', true))
            );
            """,
        ),
    ]
