import django_filters

from apps.profiles.models import BloodGroup

from .models import BloodRequest, BloodRequestStatus


class BloodRequestFilter(django_filters.FilterSet):
    blood_group = django_filters.ChoiceFilter(field_name="blood_group", choices=BloodGroup.choices)
    status = django_filters.ChoiceFilter(field_name="status", choices=BloodRequestStatus.choices)
    location = django_filters.CharFilter(field_name="location", lookup_expr="icontains")

    class Meta:
        model = BloodRequest
        fields = ["blood_group", "status", "location"]