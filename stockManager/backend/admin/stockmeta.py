"""
股票元数据管理
"""
from backend.admin.base import BaseModelAdmin, StockMeta, admin
from backend.datasource.sw_industry import fetch_sw_industry_name
from backend.models import SwIndustry

_A_SHARE_TYPES = (
    StockMeta.StockType.SH60,
    StockMeta.StockType.SZ00,
    StockMeta.StockType.SZ300,
    StockMeta.StockType.SH688,
    StockMeta.StockType.BJ,
)


@admin.register(StockMeta)
class StockMetaAdmin(BaseModelAdmin):
    """股票元数据管理（全局共享）"""

    list_display = ['code', 'name', 'stockType', 'swIndustry', 'isNew']
    list_filter = ['stockType', 'swIndustry', 'isNew']
    search_fields = ['code', 'name']
    list_select_related = ('swIndustry',)

    fieldsets = (
        ('基本信息', {
            'fields': ('code', 'name', 'stockType', 'swIndustry', 'isNew')
        }),
    )
    # StockMeta 是全局共享的，所有用户都可以看到和操作

    def save_model(self, request, obj, form, change):
        self._fill_sw_industry(obj)
        super().save_model(request, obj, form, change)

    def _fill_sw_industry(self, obj: StockMeta) -> None:
        if obj.swIndustry is not None or obj.stockType not in _A_SHARE_TYPES:
            return
        name = fetch_sw_industry_name(obj.code)
        if not name:
            return
        industry = SwIndustry.objects.filter(name=name).first()
        if industry:
            obj.swIndustry = industry
