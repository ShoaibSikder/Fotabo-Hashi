from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("profiles", "0002_profile_profile_blood_group_idx_and_more")]

    operations = [
        migrations.RunSQL(
            """
            ALTER TABLE profiles_profile ENABLE ROW LEVEL SECURITY;
            ALTER TABLE profiles_profile FORCE ROW LEVEL SECURITY;
            CREATE POLICY profiles_profile_select ON profiles_profile FOR SELECT USING (
                current_setting('app.is_authenticated', true) = 'true' AND
                (current_setting('app.is_admin', true) = 'true' OR
                 user_id::text = current_setting('app.user_id', true))
            );
            CREATE POLICY profiles_profile_insert ON profiles_profile FOR INSERT WITH CHECK (
                current_setting('app.is_authenticated', true) = 'true' AND
                (current_setting('app.is_admin', true) = 'true' OR
                 user_id::text = current_setting('app.user_id', true))
            );
            CREATE POLICY profiles_profile_update ON profiles_profile FOR UPDATE USING (
                current_setting('app.is_authenticated', true) = 'true' AND
                (current_setting('app.is_admin', true) = 'true' OR
                 user_id::text = current_setting('app.user_id', true))
            ) WITH CHECK (
                current_setting('app.is_authenticated', true) = 'true' AND
                (current_setting('app.is_admin', true) = 'true' OR
                 user_id::text = current_setting('app.user_id', true))
            );
            """,
            """
            DROP POLICY IF EXISTS profiles_profile_update ON profiles_profile;
            DROP POLICY IF EXISTS profiles_profile_insert ON profiles_profile;
            DROP POLICY IF EXISTS profiles_profile_select ON profiles_profile;
            ALTER TABLE profiles_profile NO FORCE ROW LEVEL SECURITY;
            ALTER TABLE profiles_profile DISABLE ROW LEVEL SECURITY;
            """,
        ),
    ]
