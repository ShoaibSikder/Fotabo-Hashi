from django.db import transaction

from .models import Profile


@transaction.atomic
def update_profile(*, profile: Profile, **data) -> Profile:
    for field, value in data.items():
        setattr(profile, field, value)

    profile.save()
    return profile