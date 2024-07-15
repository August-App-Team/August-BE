from django.urls import path

from apps.users.views import (
    CheckRegisteredView,
    GoogleLoginAndroidCallbackView,
    GoogleLoginView,
    GoogleLoginCallbackView,
    GoogleLoginiOSCallbackView,
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
        "google/login/callback/ios/",
        GoogleLoginiOSCallbackView.as_view(),
        name="google_login_ios_callback",
    ),
    path(
        "google/login/callback/android/",
        GoogleLoginAndroidCallbackView.as_view(),
        name="google_login_android_callback",
    ),
    path("registered/", CheckRegisteredView.as_view(), name="check_registered"),
    path("<int:pk>/", UserView.as_view(), name="user_detail"),
    path("me/", UserDetailsView.as_view(), name="user_detail_logged_in"),
]
