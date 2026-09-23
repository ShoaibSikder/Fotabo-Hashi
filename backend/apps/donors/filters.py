import django_filters

from apps.profiles.models import BloodGroup, Profile


class DonorFilter(django_filters.FilterSet):
    blood_group = django_filters.ChoiceFilter(
        field_name="blood_group",
        choices=BloodGroup.choices,
    )
    location = django_filters.CharFilter(field_name="location", lookup_expr="icontains")
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = Profile
        fields = ["blood_group", "location", "name"]