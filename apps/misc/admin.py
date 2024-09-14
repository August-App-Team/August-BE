from django.contrib import admin

from apps.misc.models import AppStoreLink, MinSupportedVersion


class AppStoreLinkAdmin(admin.ModelAdmin):
    list_display = ("platform", "link")


class MinSupportedVersionAdmin(admin.ModelAdmin):
    list_display = ("platform", "version")


admin.site.register(AppStoreLink, AppStoreLinkAdmin)
admin.site.register(MinSupportedVersion, MinSupportedVersionAdmin)
