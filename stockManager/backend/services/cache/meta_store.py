"""股票元数据与名称同步标记缓存"""
from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from ...common import logger
from ...common.types import RealtimePriceDict
from ...models import StockMeta as StockMetaModel
from . import keys


def clear_stock_meta_all() -> None:
    cache.delete(keys.KEY_STOCK_META_ALL)


def get_stock_meta_dict() -> dict[str, StockMetaModel]:
    cached = cache.get(keys.KEY_STOCK_META_ALL)
    if cached:
        return {
            code: StockMetaModel(
                code=data["code"],
                name=data.get("name", ""),
                isNew=data["isNew"],
                stockType=data["stockType"],
            )
            for code, data in cached.items()
        }
    meta_dict = {meta.code: meta for meta in StockMetaModel.objects.all()}
    cache.set(
        keys.KEY_STOCK_META_ALL,
        {
            code: {
                "code": meta.code,
                "name": meta.name,
                "isNew": meta.isNew,
                "stockType": meta.stockType,
            }
            for code, meta in meta_dict.items()
        },
        keys.TTL_STOCK_META,
    )
    return meta_dict


def sync_names_from_realtime(prices: RealtimePriceDict) -> int:
    if not prices or cache.get(keys.KEY_STOCK_NAME_SYNC_MARK) is not None:
        return 0

    name_map = {
        code: name
        for code, price_data in prices.items()
        if (name := (price_data.get("name") or "").strip())
    }
    if not name_map:
        return 0

    changed_metas = []
    for meta in StockMetaModel.objects.filter(code__in=name_map.keys()):
        latest_name = name_map.get(meta.code, "")
        if latest_name and latest_name != meta.name:
            meta.name = latest_name
            changed_metas.append(meta)

    cache.set(keys.KEY_STOCK_NAME_SYNC_MARK, True, keys.TTL_STOCK_NAME_SYNC)
    if not changed_metas:
        return 0

    StockMetaModel.objects.bulk_update(changed_metas, ["name"])
    clear_stock_meta_all()
    logger.debug(f"股票名称同步完成，更新 {len(changed_metas)} 条记录")
    return len(changed_metas)


@receiver([post_save, post_delete], sender=StockMetaModel)
def clear_stock_meta_on_model_change(sender, instance, **kwargs) -> None:
    clear_stock_meta_all()
    logger.info("清除股票元数据 Redis 缓存")
