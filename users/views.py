from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from drf_yasg.utils import swagger_auto_schema
from .models import User, Opportunity
from .serializers import UserSerializer, OpportunitySerializer, LoginSerializer, TokenSerializer, ChangePasswordSerializer
from rest_framework_simplejwt.tokens import RefreshToken

@swagger_auto_schema(
    request_body=UserSerializer,
    responses={201: UserSerializer()}
)
class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

userListCreateView = UserListCreateView.as_view()


@swagger_auto_schema(
    request_body=UserSerializer,
    responses={200: UserSerializer()}
)
class UserRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

userRetrieveUpdateDestroyView = UserRetrieveUpdateDestroyView.as_view()




class LoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        request_body=LoginSerializer,
        responses={200: TokenSerializer(), 401: 'Invalid credentials'}
    )
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, username=email, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

loginAPIView = LoginAPIView.as_view()


class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        responses={200: UserSerializer()}
    )
    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

userProfileView = UserProfileView.as_view()


class ChangePasswordView(generics.UpdateAPIView):
    """
    An endpoint for changing password.
    """
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

changePasswordView = ChangePasswordView.as_view()


@swagger_auto_schema(
    request_body=OpportunitySerializer,
    responses={201: OpportunitySerializer()}
)
class OpportunityListCreateView(generics.ListCreateAPIView):
    queryset = Opportunity.objects.all()
    serializer_class = OpportunitySerializer
    permission_classes = [permissions.AllowAny]

opportunityListCreateView = OpportunityListCreateView.as_view()


@swagger_auto_schema(
    request_body=OpportunitySerializer,
    responses={200: OpportunitySerializer()}
)
class OpportunityDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Opportunity.objects.all()
    serializer_class = OpportunitySerializer
    permission_classes = [permissions.AllowAny]

opportunityDetailView = OpportunityDetailView.as_view()
