from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .serialazers import ActivationSerialazer, ChangePasswordSerialazer, LoginSerialazer, RegistrationSerializer, \
    ForgotPasswordSerialazer, ForgotPasswordCompleteSerializer


class ActivationView(APIView):
    def post(self, request):
        serializer = ActivationSerialazer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.activate()
            return Response('Account was successfully activated', status=status.HTTP_200_OK)
        return Response('Check you\'re data')


class ChangePasswordView(APIView):
    def post(self, request):
        serializer = ChangePasswordSerialazer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.set_new_password()
            return Response('Password was successfully updated')


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        Token.objects.filter(user=user).delete()
        return Response('You successfully logged out')


class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerialazer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.send_verification_mail()
            return Response('We\'ve send you mail with recovery code')


class ForgotPasswordCompleteView(APIView):
    def post(self, request):
        serializer = ForgotPasswordCompleteSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.set_new_password()
            return Response('Password was successfully updated')


class RegistrationView(APIView):
    def post(self, request):
        data = request.data
        serializer = RegistrationSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.create(serializer.validated_data)
            return Response('Account was successfully created', status=status.HTTP_201_CREATED)


class LoginView(ObtainAuthToken):
    serializer_class = LoginSerialazer
