from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter

class GoogleiOSOAuth2Adapter(GoogleOAuth2Adapter):
    provider_id = "google_ios"

class GoogleAndroidOAuth2Adapter(GoogleOAuth2Adapter):
    provider_id = "google_android"

class GoogleWebOAuth2Adapter(GoogleOAuth2Adapter):
    provider_id = "google_web"