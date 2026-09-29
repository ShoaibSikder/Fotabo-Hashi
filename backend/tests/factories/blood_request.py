import factory

from apps.blood_requests.models import BloodRequest, BloodRequestStatus
from apps.profiles.models import BloodGroup

from .user import UserFactory


class BloodRequestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BloodRequest

    requester = factory.SubFactory(UserFactory)
    blood_group = BloodGroup.O_POSITIVE
    required_units = 1
    location = "Dhaka"
    description = "Urgent blood requirement."
    status = BloodRequestStatus.ACTIVE
