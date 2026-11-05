from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("profiles", "0009_profile_login_read"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="is_available_for_donation",
            field=models.BooleanField(default=True),
        ),
    ]
