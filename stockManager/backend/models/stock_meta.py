from django.db import models
from django.utils.translation import gettext_lazy as _


class StockMeta(models.Model):
    """股票元数据模型（全局共享）"""

    class StockType(models.TextChoices):
        SH60 = "SH60", _("沪市")
        SZ00 = "SZ00", _("深市")
        SZ300 = "SZ300", _("创业板")
        SH688 = "SH688", _("科创板")
        BJ = "BJ", _("北交所")
        CONV = "CONV", _("可转债")
        FUNDIN = "FUNDIN", _("场内基金")
        FUNDAB = "FUNDAB", _("分级基金")
        HK = "HK", _("港股通")
        OTHER = "OTHER", _("其它")

    code = models.CharField(max_length=200, unique=True, verbose_name="股票代码")
    name = models.CharField(max_length=64, blank=True, default="", verbose_name="股票名称")
    isNew = models.BooleanField(default=False, verbose_name="是否新股")
    stockType = models.CharField(  # type: ignore[misc]
        max_length=6,
        choices=StockType.choices,
        default=StockType.OTHER,
        verbose_name="股票类型"
    )

    class Meta:
        verbose_name = "股票元数据"
        verbose_name_plural = "股票元数据"

    def __str__(self) -> str:
        display_name = self.name or self.code
        return f"{self.code} ({display_name}) - {self.get_stockType_display()}"  # type: ignore[attr-defined]
