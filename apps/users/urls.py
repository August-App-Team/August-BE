from django.urls import path

from apps.users.views import (
    AppleLoginCallbackView,
    CheckRegisteredView,
    GoogleLoginView,
    GoogleLoginCallbackView,
    LogoutDeleteView,
    SetDefaultProfileImageView,
    UserView,
    UserDetailsView,
)


urlpatterns = [
    path("google/login/", GoogleLoginView.as_view(), name="google_login"),
    path(
        "google/login/callback/",
        GoogleLoginCallbackView.as_view(),
        name="google_login_callback",
    ),
    path(
        "apple/login/callback/",
        AppleLoginCallbackView.as_view(),
        name="apple_login_callback",
    ),
    path("registered/", CheckRegisteredView.as_view(), name="check_registered"),
    path("<int:pk>/", UserView.as_view(), name="user_detail"),
    path("me/", UserDetailsView.as_view(), name="user_detail_logged_in"),
    path("me/profile-image/reset/", SetDefaultProfileImageView.as_view(), name="reset_profile_image"),
    path("me/delete/", LogoutDeleteView.as_view(), name="user_delete"),
]
