from django.contrib.auth.models import User
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .serializers import RegisterSerializer, UserProfileSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Extending default JWT serializer to include info of user in login response.
    """

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
        }
        return data

class LoginView(TokenObtainPairView):
    """
    POST /api/auth/login
    login with username and password and returns jwt access + refresh tokens.
    """
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    """
    POST /api/auth/register/
    register a new user account
    """
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # auto issue tokens on successful registration
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'User registered successfully.',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            },
            'tokens': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)

class LogoutView(APIView):
        """
        POST /api/auth/logout/
        blacklist the refresh token to log out
        """
        permission_classes = [IsAuthenticated]

        def post(self, request):
            try:
                refresh_token = request.data.get('refresh')
                if not refresh_token:
                    return Response({
                        'error': 'Refresh token is required.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response({
                    'message': 'Logged out successfully.'
                }, status=status.HTTP_200_OK)
            except Exception:
                return Response({
                    'error': 'Invalid token.'
                }, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(generics.RetrieveUpdateAPIView):
    """
    GET /api/auth/profile/ - View your profile
    PUT /api/auth/profile/ - Update your profile
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user
