from django.urls import path

from apps.misc.views import MinSupportedVersionView

urlpatterns = [
    path('min-supported-version/', MinSupportedVersionView.as_view(), name='min-supported-version'),
]