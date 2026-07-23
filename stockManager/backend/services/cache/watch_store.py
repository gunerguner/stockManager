"""用户关注列表缓存"""
from typing import cast

from django.contrib.auth.models import User
from django.core.cache import cache
from django.db.models import F
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from backend.common.types import WatchItemDict
from backend.models import WatchItem
from backend.services.cache import keys


def get_user_watchlist(user: User) -> list[WatchItemDict]:
    key = keys.KEY_USER_WATCHLIST.format(user_id=user.pk)
    cached = cache.get(key)
    if cached is not None:
        return cached
    items = cast(
        list[WatchItemDict],
        list(
            WatchItem.objects.filter(user=user)
            .annotate(code=F('stock_meta__code'))
            .values(
                "code",
                "risk",
                "opportunity",
                "leftPoint",
                "trendPoint",
                "bloodPoint",
                "hidden",
            )
        ),
    )
    cache.set(key, items, keys.TTL_USER_DATA)
    return items


def clear_user_watchlist(user_id: int) -> None:
    cache.delete(keys.KEY_USER_WATCHLIST.format(user_id=user_id))


@receiver([post_save, post_delete], sender=WatchItem)
def clear_watchlist_on_change(sender, instance, **kwargs) -> None:
    clear_user_watchlist(instance.user_id)
