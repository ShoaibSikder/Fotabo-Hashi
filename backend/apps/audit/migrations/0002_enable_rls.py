from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("audit", "0001_initial")]

    operations = [
        migrations.RunSQL(
            """
            ALTER TABLE audit_auditlog ENABLE ROW LEVEL SECURITY;
            ALTER TABLE audit_auditlog FORCE ROW LEVEL SECURITY;
            CREATE POLICY audit_admin_read ON audit_auditlog FOR SELECT USING (
                current_setting('app.is_admin', true) = 'true'
            );
            CREATE POLICY audit_authenticated_insert ON audit_auditlog FOR INSERT WITH CHECK (
                current_setting('app.is_authenticated', true) = 'true'
            );
            """,
            """
            DROP POLICY IF EXISTS audit_authenticated_insert ON audit_auditlog;
            DROP POLICY IF EXISTS audit_admin_read ON audit_auditlog;
            ALTER TABLE audit_auditlog NO FORCE ROW LEVEL SECURITY;
            ALTER TABLE audit_auditlog DISABLE ROW LEVEL SECURITY;
            """,
        ),
    ]
