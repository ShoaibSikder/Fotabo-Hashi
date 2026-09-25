from django.apps import AppConfig


class CommonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.common"

    def ready(self):
        from django.conf import settings
        from django.db.backends.signals import connection_created

        if not getattr(settings, "RLS_TEST_MODE", False):
            return

        from infrastructure.database.rls.constants import (
            RLS_IS_ADMIN,
            RLS_IS_AUTHENTICATED,
            RLS_LOGIN_EMAIL,
            RLS_USER_ID,
        )

        def configure_test_connection(sender, connection, **kwargs):
            if connection.vendor != "postgresql":
                return
            with connection.cursor() as cursor:
                for name, value in (
                    (RLS_USER_ID, ""),
                    (RLS_IS_ADMIN, "true"),
                    (RLS_IS_AUTHENTICATED, "true"),
                    (RLS_LOGIN_EMAIL, ""),
                ):
                    cursor.execute("SELECT set_config(%s, %s, false)", [name, value])

        connection_created.connect(configure_test_connection, weak=False)
