from django.shortcuts import redirect
from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from django_user_agents.utils import get_user_agent

from apps.misc.models import AppStoreLink, MinSupportedVersion

CACHE_KEY = "app_store_links"


def get_store_links():
    app_store_links = cache.get(CACHE_KEY)

    if not app_store_links:
        app_store_links = {
            "ios": AppStoreLink.objects.filter(platform="ios").first().link,
            "android": AppStoreLink.objects.filter(platform="android").first().link,
        }
        cache.set(CACHE_KEY, app_store_links, timeout=86400)  # Cache for 1 day

    return app_store_links


def redirect_to_app_store_view(request):
    user_agent = get_user_agent(request)
    platform = user_agent.os.family.lower()
    app_store_links = get_store_links()

    if platform == "ios":
        return redirect(app_store_links["ios"])
    elif platform == "android":
        return redirect(app_store_links["android"])
    else:
        return redirect("https://support.augustapp.one/")


class MinSupportedVersionView(APIView):
    def get(self, request, *args, **kwargs):
        platform = request.query_params.get("platform")
        if not platform:
            return Response(
                {"error": "Query parameter 'platform' is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        min_supported_version = MinSupportedVersion.objects.filter(
            platform=platform
        ).first()

        if min_supported_version:
            return Response({"version": min_supported_version.version})
        else:
            return Response(
                {"error": "Invalid platform."}, status=status.HTTP_400_BAD_REQUEST
            )
