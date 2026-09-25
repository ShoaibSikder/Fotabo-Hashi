from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("accounts", "0001_initial")]

    operations = [
        migrations.RunSQL(
            """
            ALTER TABLE accounts_user ENABLE ROW LEVEL SECURITY;
            ALTER TABLE accounts_user FORCE ROW LEVEL SECURITY;
            CREATE POLICY accounts_user_select ON accounts_user FOR SELECT USING (
                (current_setting('app.is_authenticated', true) = 'true' AND
                 (current_setting('app.is_admin', true) = 'true' OR
                  id::text = current_setting('app.user_id', true))) OR
                email = current_setting('app.login_email', true)
            );
            CREATE POLICY accounts_user_insert ON accounts_user FOR INSERT WITH CHECK (
                current_setting('app.is_admin', true) = 'true'
            );
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
            """
            DROP POLICY IF EXISTS accounts_user_update ON accounts_user;
            DROP POLICY IF EXISTS accounts_user_insert ON accounts_user;
            DROP POLICY IF EXISTS accounts_user_select ON accounts_user;
            ALTER TABLE accounts_user NO FORCE ROW LEVEL SECURITY;
            ALTER TABLE accounts_user DISABLE ROW LEVEL SECURITY;
            """,
        ),
    ]
