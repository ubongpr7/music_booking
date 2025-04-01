
from rest_framework.response import Response
from rest_framework import status
from mainapps.accounts.api.serializers import UserCreateSerializer

from rest_framework import generics, status

class UserRegistrationAPIView(generics.CreateAPIView):
    """
    Create new user with first name, email, and password
    """
    serializer_class = UserCreateSerializer
    authentication_classes = []
    permission_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )