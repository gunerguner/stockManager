"""股票元数据与名称同步标记缓存"""
from django.core.cache import cache

from ...models import StockMeta as StockMetaModel
from . import keys


def get_stock_meta_all_cache() -> dict | None:
    return cache.get(keys.KEY_STOCK_META_ALL)


def set_stock_meta_all_cache(meta_dict: dict) -> None:
    cache.set(
        keys.KEY_STOCK_META_ALL,
        {
            code: {
                'code': meta.code,
                'name': meta.name,
                'isNew': meta.isNew,
                'stockType': meta.stockType,
            }
            for code, meta in meta_dict.items()
        },
        keys.TTL_STOCK_META,
    )


def clear_stock_meta_all() -> None:
    cache.delete(keys.KEY_STOCK_META_ALL)


def has_stock_name_synced() -> bool:
    return cache.get(keys.KEY_STOCK_NAME_SYNC_MARK) is not None


def mark_stock_name_synced() -> None:
    cache.set(keys.KEY_STOCK_NAME_SYNC_MARK, True, keys.TTL_STOCK_NAME_SYNC)


def get_stock_meta_dict() -> dict[str, StockMetaModel]:
    cached_data = get_stock_meta_all_cache()
    if cached_data:
        return {
            code: StockMetaModel(
                code=data['code'],
                name=data.get('name', ''),
                isNew=data['isNew'],
                stockType=data['stockType'],
            )
            for code, data in cached_data.items()
        }
    meta_dict = {meta.code: meta for meta in StockMetaModel.objects.all()}
    set_stock_meta_all_cache(meta_dict)
    return meta_dict
