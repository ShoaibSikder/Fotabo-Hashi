import django_filters
from django.db.models import Q

from apps.profiles.models import BloodGroup, Profile


class DonorFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")
    blood_group = django_filters.ChoiceFilter(
        field_name="blood_group",
        choices=BloodGroup.choices,
    )
    location = django_filters.CharFilter(field_name="location", lookup_expr="icontains")
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")

    @staticmethod
    def filter_search(queryset, name, value):
        value = value.strip()
        if not value:
            return queryset

        return queryset.filter(
            Q(name__icontains=value)
            | Q(location__icontains=value)
            | Q(blood_group__iexact=value)
        )

    class Meta:
        model = Profile
        fields = ["search", "blood_group", "location", "name"]
