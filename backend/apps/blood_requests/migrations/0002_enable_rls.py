from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("blood_requests", "0001_initial")]

    operations = [
        migrations.RunSQL(
            """
            ALTER TABLE blood_requests_bloodrequest ENABLE ROW LEVEL SECURITY;
            ALTER TABLE blood_requests_bloodrequest FORCE ROW LEVEL SECURITY;
            CREATE POLICY blood_requests_select ON blood_requests_bloodrequest FOR SELECT USING (
                current_setting('app.is_authenticated', true) = 'true'
            );
            CREATE POLICY blood_requests_insert ON blood_requests_bloodrequest FOR INSERT WITH CHECK (
                current_setting('app.is_authenticated', true) = 'true' AND
                (current_setting('app.is_admin', true) = 'true' OR
                 requester_id::text = current_setting('app.user_id', true))
            );
            CREATE POLICY blood_requests_update ON blood_requests_bloodrequest FOR UPDATE USING (
                current_setting('app.is_authenticated', true) = 'true' AND
                (current_setting('app.is_admin', true) = 'true' OR
                 requester_id::text = current_setting('app.user_id', true))
            ) WITH CHECK (
                current_setting('app.is_authenticated', true) = 'true' AND
                (current_setting('app.is_admin', true) = 'true' OR
                 requester_id::text = current_setting('app.user_id', true))
            );
            CREATE POLICY blood_requests_delete ON blood_requests_bloodrequest FOR DELETE USING (
                current_setting('app.is_authenticated', true) = 'true' AND
                (current_setting('app.is_admin', true) = 'true' OR
                 requester_id::text = current_setting('app.user_id', true))
            );
            """,
            """
            DROP POLICY IF EXISTS blood_requests_delete ON blood_requests_bloodrequest;
            DROP POLICY IF EXISTS blood_requests_update ON blood_requests_bloodrequest;
            DROP POLICY IF EXISTS blood_requests_insert ON blood_requests_bloodrequest;
            DROP POLICY IF EXISTS blood_requests_select ON blood_requests_bloodrequest;
            ALTER TABLE blood_requests_bloodrequest NO FORCE ROW LEVEL SECURITY;
            ALTER TABLE blood_requests_bloodrequest DISABLE ROW LEVEL SECURITY;
            """,
        ),
    ]
