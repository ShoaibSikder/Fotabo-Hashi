import factory

from apps.content.models import Notice, OrganizationInformation


class NoticeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Notice

    title = factory.Sequence(lambda number: f"Notice {number}")
    content = "Public content."
    is_published = True


class OrganizationInformationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrganizationInformation

    name = "Fotabo Hashi"
    description = "Blood donation platform."
