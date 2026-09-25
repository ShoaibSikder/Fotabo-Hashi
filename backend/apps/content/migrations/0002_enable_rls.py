from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("content", "0001_initial")]

    operations = [
        migrations.RunSQL(
            """
            ALTER TABLE content_organizationinformation ENABLE ROW LEVEL SECURITY;
            ALTER TABLE content_organizationinformation FORCE ROW LEVEL SECURITY;
            CREATE POLICY organization_public_read ON content_organizationinformation
                FOR SELECT USING (true);
            CREATE POLICY organization_admin_write ON content_organizationinformation
                FOR ALL USING (current_setting('app.is_admin', true) = 'true')
                WITH CHECK (current_setting('app.is_admin', true) = 'true');

            ALTER TABLE content_notice ENABLE ROW LEVEL SECURITY;
            ALTER TABLE content_notice FORCE ROW LEVEL SECURITY;
            CREATE POLICY notice_public_read ON content_notice
                FOR SELECT USING (is_published = true);
            CREATE POLICY notice_admin_access ON content_notice
                FOR ALL USING (current_setting('app.is_admin', true) = 'true')
                WITH CHECK (current_setting('app.is_admin', true) = 'true');

            ALTER TABLE content_foundingmember ENABLE ROW LEVEL SECURITY;
            ALTER TABLE content_foundingmember FORCE ROW LEVEL SECURITY;
            CREATE POLICY founding_member_public_read ON content_foundingmember
                FOR SELECT USING (is_published = true);
            CREATE POLICY founding_member_admin_access ON content_foundingmember
                FOR ALL USING (current_setting('app.is_admin', true) = 'true')
                WITH CHECK (current_setting('app.is_admin', true) = 'true');

            ALTER TABLE content_slideritem ENABLE ROW LEVEL SECURITY;
            ALTER TABLE content_slideritem FORCE ROW LEVEL SECURITY;
            CREATE POLICY slider_public_read ON content_slideritem
                FOR SELECT USING (is_published = true);
            CREATE POLICY slider_admin_access ON content_slideritem
                FOR ALL USING (current_setting('app.is_admin', true) = 'true')
                WITH CHECK (current_setting('app.is_admin', true) = 'true');
            """,
            """
            DROP POLICY IF EXISTS slider_admin_access ON content_slideritem;
            DROP POLICY IF EXISTS slider_public_read ON content_slideritem;
            ALTER TABLE content_slideritem NO FORCE ROW LEVEL SECURITY;
            ALTER TABLE content_slideritem DISABLE ROW LEVEL SECURITY;
            DROP POLICY IF EXISTS founding_member_admin_access ON content_foundingmember;
            DROP POLICY IF EXISTS founding_member_public_read ON content_foundingmember;
            ALTER TABLE content_foundingmember NO FORCE ROW LEVEL SECURITY;
            ALTER TABLE content_foundingmember DISABLE ROW LEVEL SECURITY;
            DROP POLICY IF EXISTS notice_admin_access ON content_notice;
            DROP POLICY IF EXISTS notice_public_read ON content_notice;
            ALTER TABLE content_notice NO FORCE ROW LEVEL SECURITY;
            ALTER TABLE content_notice DISABLE ROW LEVEL SECURITY;
            DROP POLICY IF EXISTS organization_admin_write ON content_organizationinformation;
            DROP POLICY IF EXISTS organization_public_read ON content_organizationinformation;
            ALTER TABLE content_organizationinformation NO FORCE ROW LEVEL SECURITY;
            ALTER TABLE content_organizationinformation DISABLE ROW LEVEL SECURITY;
            """,
        ),
    ]
