from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.shortcuts import redirect
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.apple.views import AppleOAuth2Adapter
from allauth.socialaccount.providers.apple.client import AppleOAuth2Client
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView

from apps.users.oauth2_adapters import (
    GoogleAndroidOAuth2Adapter,
    GoogleWebOAuth2Adapter,
    GoogleiOSOAuth2Adapter,
)
from apps.users.permissions import IsHimselfOrAdmin
from apps.users.serializers import CustomUserDetailsSerializer, FullUserSerializer
from config.settings.base import get_secret


class GoogleLoginView(APIView):
    def get(self, request, *args, **kwargs):
        client_id = get_secret("GOOGLE_WEB_CLIENT_ID")
        redirect_uri = get_secret("DEPLOY_HOST_PORT") + "/users/google/login/callback/"
        response_type = "code"
        scope = "profile%20email"
        url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&redirect_uri={redirect_uri}&response_type={response_type}&scope={scope}"
        return redirect(url)


# use authorization code grant - one that receives 'code' from client (web app)
class GoogleLoginCallbackView(SocialLoginView):
    adapter_class = GoogleWebOAuth2Adapter
    callback_url = get_secret("DEPLOY_HOST_PORT") + "/users/google/login/callback/"
    client_class = OAuth2Client

    def get(self, request, *args, **kwargs):
        code = request.query_params.get("code", None)
        error = request.query_params.get("error", None)
        if error:
            return Response(data={"error": error}, status=status.HTTP_400_BAD_REQUEST)

        self.request.data.update({"code": code})

        return self.post(request, args, kwargs)


# to use implicit grant - one that receives 'access_token' from client app
class GoogleLoginiOSCallbackView(SocialLoginView):
    adapter_class = GoogleiOSOAuth2Adapter


# implicit grant
class GoogleLoginAndroidCallbackView(SocialLoginView):
    adapter_class = GoogleAndroidOAuth2Adapter


class AppleLoginCallbackView(SocialLoginView):
    adapter_class = AppleOAuth2Adapter
    callback_url = get_secret("DEPLOY_HOST_PORT") + "/users/apple/login/callback/"
    client_class = AppleOAuth2Client


class CheckRegisteredView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")

        try:
            validate_email(email)
        except ValidationError as ve:
            return Response(
                data={"error": ve.message}, status=status.HTTP_400_BAD_REQUEST
            )

        exists = get_user_model().objects.filter(email=email).exists()

        return Response(data={"registered": exists})


class UserView(generics.RetrieveUpdateAPIView):
    queryset = get_user_model().objects.all()
    permission_classes = [IsHimselfOrAdmin]

    def get_serializer_class(self):
        if self.request.user.is_staff:
            return FullUserSerializer
        return CustomUserDetailsSerializer

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except ValidationError as ve:
            return Response(data=dict(ve), status=status.HTTP_400_BAD_REQUEST)


class UserDetailsView(generics.RetrieveUpdateAPIView):
    serializer_class = CustomUserDetailsSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def get_queryset(self):
        """
        Adding this method since it is sometimes called when using
        django-rest-swagger
        """
        return get_user_model().objects.none()

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except ValidationError as ve:
            return Response(data=dict(ve), status=status.HTTP_400_BAD_REQUEST)

class SetDefaultProfileImageView(generics.CreateAPIView):
    class UserProfileImageSerializer(CustomUserDetailsSerializer):
        class Meta(CustomUserDetailsSerializer.Meta):
            fields = ("profile_image", )
            read_only_fields = ("profile_image",)

    permission_classes = (IsAuthenticated, )
    serializer_class = UserProfileImageSerializer

    def post(self, request, *args, **kwargs):
        user = request.user
        user.profile_image_file.name = get_user_model().DEFAULT_PROFILE_IMAGE
        user.profile_image_url = ""
        user.save()
        serializer = self.get_serializer(instance=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)