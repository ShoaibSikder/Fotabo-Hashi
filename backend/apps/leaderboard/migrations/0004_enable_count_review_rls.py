from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("leaderboard", "0003_donationcountreview")]

    operations = [
        migrations.RunSQL(
            """
            ALTER TABLE leaderboard_donationcountreview ENABLE ROW LEVEL SECURITY;
            ALTER TABLE leaderboard_donationcountreview FORCE ROW LEVEL SECURITY;
            CREATE POLICY leaderboard_count_review_select ON leaderboard_donationcountreview FOR SELECT USING (
                current_setting('app.is_authenticated', true) = 'true' AND
                (current_setting('app.is_admin', true) = 'true' OR
                 user_id::text = current_setting('app.user_id', true))
            );
            CREATE POLICY leaderboard_count_review_insert ON leaderboard_donationcountreview FOR INSERT WITH CHECK (
                current_setting('app.is_authenticated', true) = 'true' AND
                (current_setting('app.is_admin', true) = 'true' OR
                 user_id::text = current_setting('app.user_id', true))
            );
            CREATE POLICY leaderboard_count_review_update ON leaderboard_donationcountreview FOR UPDATE USING (
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
            DROP POLICY IF EXISTS leaderboard_count_review_update ON leaderboard_donationcountreview;
            DROP POLICY IF EXISTS leaderboard_count_review_insert ON leaderboard_donationcountreview;
            DROP POLICY IF EXISTS leaderboard_count_review_select ON leaderboard_donationcountreview;
            ALTER TABLE leaderboard_donationcountreview NO FORCE ROW LEVEL SECURITY;
            ALTER TABLE leaderboard_donationcountreview DISABLE ROW LEVEL SECURITY;
            """,
        ),
    ]
