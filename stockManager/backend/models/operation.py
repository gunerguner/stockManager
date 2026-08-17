from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from .stock_meta import StockMeta


class Operation(models.Model):
    """股票操作记录模型"""

    class OperationType(models.TextChoices):
        BUY = "BUY", _("买入")
        SELL = "SELL", _("卖出")
        Dividend = "DV", _("除权除息")

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='operations', verbose_name="用户")
    stock_meta = models.ForeignKey(
        StockMeta,
        on_delete=models.PROTECT,
        related_name='operations',
        verbose_name="股票",
    )
    date = models.DateField(verbose_name="交易日期")
    sortOrder = models.PositiveIntegerField(default=0, verbose_name="同日顺序")
    operationType = models.CharField(  # type: ignore[misc]
        max_length=4,
        choices=OperationType.choices,
        default=OperationType.BUY,
        verbose_name="操作类型"
    )
    price = models.DecimalField(
        max_digits=16,
        decimal_places=4,
        default=Decimal("0"),
        verbose_name="价格",
    )
    count = models.IntegerField(default=0, blank=True, verbose_name="数量")
    fee = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0"),
        verbose_name="手续费",
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="成交金额(人民币)",
        help_text="仅港股通买卖填写；非港股留空",
    )
    comment = models.CharField(max_length=200, blank=True, verbose_name="备注")
    cash = models.DecimalField(
        max_digits=16,
        decimal_places=6,
        default=Decimal("0"),
        verbose_name="分红",
    )
    stock = models.FloatField(default=0, verbose_name="送股")
    reserve = models.FloatField(default=0, verbose_name="转增")

    class Meta:
        verbose_name = "股票操作记录"
        verbose_name_plural = "股票操作记录"
        ordering = ['date', 'sortOrder', 'id']

    def __str__(self) -> str:
        return (
            f"{self.user.username} - {self.stock_meta.code} "
            f"{self.date} {self.operationType} {self.count}"
        )
