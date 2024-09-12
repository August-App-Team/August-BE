from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache  # the default cache

from apps.misc.models import AppStoreLink


CACHE_KEY = "app_store_links"


@receiver(post_save, sender=AppStoreLink)
@receiver(post_delete, sender=AppStoreLink)
def invalidate_cache(sender, instance, **kwargs):
    """
    Invalidate cache when AppStoreLink instance is created, updated or deleted
    """
    cache.delete(CACHE_KEY)
