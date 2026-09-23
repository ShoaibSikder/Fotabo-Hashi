from django.db import transaction

from apps.common.exceptions.exceptions import BusinessRuleViolation

from .models import BloodRequest, BloodRequestStatus


@transaction.atomic
def create_blood_request(*, requester, blood_group, required_units, location, description=""):
    return BloodRequest.objects.create(
        requester=requester,
        blood_group=blood_group,
        required_units=required_units,
        location=location,
        description=description,
    )


@transaction.atomic
def update_blood_request(*, blood_request, **data):
    if blood_request.status != BloodRequestStatus.ACTIVE:
        raise BusinessRuleViolation("Only active blood requests can be updated.")
    for field, value in data.items():
        setattr(blood_request, field, value)
    blood_request.save()
    return blood_request


@transaction.atomic
def fulfill_blood_request(*, blood_request: BloodRequest) -> BloodRequest:
    if blood_request.status != BloodRequestStatus.ACTIVE:
        raise BusinessRuleViolation("Only active blood requests can be fulfilled.")
    blood_request.status = BloodRequestStatus.FULFILLED
    blood_request.save(update_fields=["status", "updated_at"])
    return blood_request


@transaction.atomic
def cancel_blood_request(*, blood_request: BloodRequest) -> BloodRequest:
    if blood_request.status != BloodRequestStatus.ACTIVE:
        raise BusinessRuleViolation("Only active blood requests can be cancelled.")
    blood_request.status = BloodRequestStatus.CANCELLED
    blood_request.save(update_fields=["status", "updated_at"])
    return blood_request