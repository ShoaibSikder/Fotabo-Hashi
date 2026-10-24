from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("notifications", "0001_initial")]

    operations = [
        migrations.RunSQL(
            """
            ALTER TABLE notifications_notification ENABLE ROW LEVEL SECURITY;
            ALTER TABLE notifications_notification FORCE ROW LEVEL SECURITY;
            CREATE POLICY notification_recipient_read ON notifications_notification
                FOR SELECT USING (
                    current_setting('app.is_admin', true) = 'true'
                    OR (
                        current_setting('app.is_authenticated', true) = 'true'
                        AND recipient_id::text = current_setting('app.user_id', true)
                    )
                );
            CREATE POLICY notification_recipient_insert ON notifications_notification
                FOR INSERT WITH CHECK (
                    current_setting('app.is_admin', true) = 'true'
                    OR (
                        current_setting('app.is_authenticated', true) = 'true'
                        AND recipient_id::text = current_setting('app.user_id', true)
                    )
                );
            CREATE POLICY notification_recipient_update ON notifications_notification
                FOR UPDATE USING (
                    current_setting('app.is_admin', true) = 'true'
                    OR recipient_id::text = current_setting('app.user_id', true)
                ) WITH CHECK (
                    current_setting('app.is_admin', true) = 'true'
                    OR recipient_id::text = current_setting('app.user_id', true)
                );
            CREATE POLICY notification_recipient_delete ON notifications_notification
                FOR DELETE USING (
                    current_setting('app.is_admin', true) = 'true'
                    OR recipient_id::text = current_setting('app.user_id', true)
                );
            """,
            """
            DROP POLICY IF EXISTS notification_recipient_delete ON notifications_notification;
            DROP POLICY IF EXISTS notification_recipient_update ON notifications_notification;
            DROP POLICY IF EXISTS notification_recipient_insert ON notifications_notification;
            DROP POLICY IF EXISTS notification_recipient_read ON notifications_notification;
            ALTER TABLE notifications_notification NO FORCE ROW LEVEL SECURITY;
            ALTER TABLE notifications_notification DISABLE ROW LEVEL SECURITY;
            """,
        )
    ]
