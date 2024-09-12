from django.contrib import admin

from apps.misc.models import AppStoreLink


class AppStoreLinkAdmin(admin.ModelAdmin):
    list_display = ("platform", "link")


admin.site.register(AppStoreLink, AppStoreLinkAdmin)
