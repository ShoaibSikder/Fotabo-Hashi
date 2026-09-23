from apps.profiles.models import Profile


def get_donor_queryset():
    return (
        Profile.objects.filter(is_available_for_donation=True)
        .select_related("user")
        .order_by("name", "id")
    )