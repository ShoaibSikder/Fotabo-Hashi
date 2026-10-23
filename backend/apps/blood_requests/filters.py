import django_filters
from django.db.models import Q

from apps.profiles.models import BloodGroup

from .models import BloodRequest, BloodRequestStatus


class BloodRequestFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")
    blood_group = django_filters.ChoiceFilter(
        field_name="blood_group", choices=BloodGroup.choices
    )
    status = django_filters.ChoiceFilter(
        field_name="status", choices=BloodRequestStatus.choices
    )
    location = django_filters.CharFilter(field_name="location", lookup_expr="icontains")

    @staticmethod
    def filter_search(queryset, name, value):
        value = value.strip()
        if not value:
            return queryset

        return queryset.filter(
            Q(blood_group__iexact=value)
            | Q(status__icontains=value)
            | Q(location__icontains=value)
            | Q(description__icontains=value)
        )

    class Meta:
        model = BloodRequest
        fields = ["search", "blood_group", "status", "location"]
