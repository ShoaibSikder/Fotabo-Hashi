from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .selectors import get_profile_for_user
from .serializers import ProfileSerializer
from .services import update_profile


class MyProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile = get_profile_for_user(user=request.user)
        return Response(ProfileSerializer(profile).data)

    def put(self, request):
        return self._update_profile(request, partial=False)

    def patch(self, request):
        return self._update_profile(request, partial=True)

    def _update_profile(self, request, *, partial):
        profile = get_profile_for_user(user=request.user)
        serializer = ProfileSerializer(profile, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        profile = update_profile(profile=profile, **serializer.validated_data)
        return Response(ProfileSerializer(profile).data)