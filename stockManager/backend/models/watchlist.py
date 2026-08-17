from django.contrib.auth.models import User
from django.db import models

from .stock_meta import StockMeta


class WatchItem(models.Model):
    """用户关注列表"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='watch_items',
        verbose_name="用户",
    )
    stock_meta = models.ForeignKey(
        StockMeta,
        on_delete=models.PROTECT,
        related_name='watch_items',
        verbose_name="股票",
    )
    risk = models.TextField(blank=True, default="", verbose_name="风险")
    opportunity = models.TextField(blank=True, default="", verbose_name="机会")
    leftPoint = models.FloatField(null=True, blank=True, verbose_name="左侧点")
    trendPoint = models.FloatField(null=True, blank=True, verbose_name="趋势点")
    bloodPoint = models.FloatField(null=True, blank=True, verbose_name="血筹点")
    comment = models.CharField(max_length=200, blank=True, default="", verbose_name="备注")
    hidden = models.BooleanField(default=False, verbose_name="是否隐藏")

    class Meta:
        verbose_name = "关注股票列表"
        verbose_name_plural = "关注股票列表"
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(fields=['user', 'stock_meta'], name='uniq_watchitem_user_stock_meta'),
        ]

    def __str__(self) -> str:
        return f"{self.user.username} - {self.stock_meta.code}"
