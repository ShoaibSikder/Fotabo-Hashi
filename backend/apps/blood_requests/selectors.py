from .models import BloodRequest


def get_blood_request_queryset():
    return (
        BloodRequest.objects.select_related("requester", "requester__profile")
        .order_by("-created_at", "-id")
    )


def get_blood_request_by_id(*, request_id):
    return get_blood_request_queryset().filter(id=request_id).first()