from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("profiles", "0003_enable_rls")]

    operations = [
        migrations.AddIndex(
            model_name="profile",
            index=models.Index(
                fields=["is_available_for_donation", "blood_group"],
                name="profile_donor_group_idx",
            ),
        ),
    ]
