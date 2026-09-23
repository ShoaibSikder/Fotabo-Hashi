from django.db import transaction

from apps.content.models import OrganizationInformation


@transaction.atomic
def create_or_update_organization_information(*, data: dict) -> OrganizationInformation:
    organization = OrganizationInformation.objects.first()
    if organization is None:
        return OrganizationInformation.objects.create(**data)
    for field, value in data.items():
        setattr(organization, field, value)
    organization.save()
    return organization