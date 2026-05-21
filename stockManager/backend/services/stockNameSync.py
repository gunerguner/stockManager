"""股票名称同步服务。"""
from typing import Dict
from ..common import logger
from ..common.types import RealtimePriceDict
from ..models import StockMeta as StockMetaModel
from .cacheRepository import CacheRepository


class StockNameSync:
    """根据实时行情结果更新 StockMeta 中的股票名称。"""

    @classmethod
    def sync_from_realtime(cls, prices: RealtimePriceDict) -> int:
        """比对实时名称和 DB 名称，批量更新变更项。"""
        if not prices:
            return 0
        if CacheRepository.has_stock_name_synced_today():
            return 0

        name_map: Dict[str, str] = {}
        for code, price_data in prices.items():
            name = (price_data.get("name") or "").strip()
            if name:
                name_map[code] = name

        if not name_map:
            return 0

        metas = StockMetaModel.objects.filter(code__in=name_map.keys())
        changed_metas = []

        for meta in metas:
            latest_name = name_map.get(meta.code, "")
            if latest_name and latest_name != meta.name:
                meta.name = latest_name
                changed_metas.append(meta)

        if not changed_metas:
            CacheRepository.mark_stock_name_synced_today()
            return 0

        StockMetaModel.objects.bulk_update(changed_metas, ["name"])
        CacheRepository.clear_stock_meta_all()
        CacheRepository.mark_stock_name_synced_today()
        logger.debug(f"股票名称同步完成，更新 {len(changed_metas)} 条记录")
        return len(changed_metas)
