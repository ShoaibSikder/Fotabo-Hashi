from rest_framework import generics, permissions

from .filters import DonorFilter
from .selectors import get_donor_queryset
from .serializers import DonorSerializer


class DonorListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DonorSerializer
    filterset_class = DonorFilter

    def get_queryset(self):
        return get_donor_queryset()