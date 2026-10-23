from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("leaderboard", "0001_initial")]

    operations = [
        migrations.RunSQL(
            """
            ALTER TABLE leaderboard_donationrecord ENABLE ROW LEVEL SECURITY;
            ALTER TABLE leaderboard_donationrecord FORCE ROW LEVEL SECURITY;
            CREATE POLICY leaderboard_donationrecord_select ON leaderboard_donationrecord FOR SELECT USING (
                current_setting('app.is_authenticated', true) = 'true' AND
                (current_setting('app.is_admin', true) = 'true' OR
                 donor_id::text = current_setting('app.user_id', true))
            );
            CREATE POLICY leaderboard_donationrecord_insert ON leaderboard_donationrecord FOR INSERT WITH CHECK (
                current_setting('app.is_admin', true) = 'true'
            );
            CREATE POLICY leaderboard_donationrecord_delete ON leaderboard_donationrecord FOR DELETE USING (
                current_setting('app.is_admin', true) = 'true'
            );
            """,
            """
            DROP POLICY IF EXISTS leaderboard_donationrecord_delete ON leaderboard_donationrecord;
            DROP POLICY IF EXISTS leaderboard_donationrecord_insert ON leaderboard_donationrecord;
            DROP POLICY IF EXISTS leaderboard_donationrecord_select ON leaderboard_donationrecord;
            ALTER TABLE leaderboard_donationrecord NO FORCE ROW LEVEL SECURITY;
            ALTER TABLE leaderboard_donationrecord DISABLE ROW LEVEL SECURITY;
            """,
        ),
    ]
