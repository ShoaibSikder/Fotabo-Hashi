from rest_framework import generics, permissions
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import BloodRequestFilter
from .selectors import get_blood_request_queryset
from .serializers import BloodRequestSerializer
from .services import (
    cancel_blood_request,
    create_blood_request,
    fulfill_blood_request,
    update_blood_request,
)


class BloodRequestListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BloodRequestSerializer
    filterset_class = BloodRequestFilter

    def get_queryset(self):
        return get_blood_request_queryset()

    def perform_create(self, serializer):
        serializer.validated_data.pop("status", None)
        serializer.instance = create_blood_request(
            requester=self.request.user,
            **serializer.validated_data,
        )


class BloodRequestDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BloodRequestSerializer

    def get_queryset(self):
        return get_blood_request_queryset()

    def perform_update(self, serializer):
        blood_request = self.get_object()
        if blood_request.requester_id != self.request.user.id:
            raise PermissionDenied("You can only update your own blood requests.")
        serializer.instance = update_blood_request(
            blood_request=blood_request,
            **serializer.validated_data,
        )


class BloodRequestActionView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    action_service = None
    ownership_message = "You can only modify your own blood requests."

    def post(self, request, pk):
        blood_request = get_blood_request_queryset().filter(pk=pk).first()
        if blood_request is None:
            raise NotFound("Blood request not found.")
        if blood_request.requester_id != request.user.id:
            raise PermissionDenied(self.ownership_message)
        blood_request = self.action_service(blood_request=blood_request)
        return Response(BloodRequestSerializer(blood_request).data)


class BloodRequestFulfillView(BloodRequestActionView):
    action_service = staticmethod(fulfill_blood_request)
    ownership_message = "You can only fulfill your own blood requests."


class BloodRequestCancelView(BloodRequestActionView):
    action_service = staticmethod(cancel_blood_request)
    ownership_message = "You can only cancel your own blood requests."