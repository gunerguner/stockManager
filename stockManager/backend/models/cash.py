from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _


class Info(models.Model):
    """用户资金信息模型"""

    class InfoType(models.TextChoices):
        ORIGIN_CASH = "originCash", _("本金")
        INCOME_CASH = "incomeCash", _("收益现金")

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='infos', verbose_name="用户")
    info_type = models.CharField(max_length=20, choices=InfoType.choices, verbose_name="类型")
    value = models.CharField(max_length=200, blank=True, verbose_name="值")

    class Meta:
        verbose_name = "用户资金信息"
        verbose_name_plural = "用户资金信息"
        unique_together = [['user', 'info_type']]

    def __str__(self) -> str:
        return f"{self.user.username} - {self.get_info_type_display()}: {self.value}"  # type: ignore[attr-defined]


class CashFlow(models.Model):
    """出入金记录模型（金额正数为入金，负数为出金）"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cash_flows',
        verbose_name="用户"
    )
    transaction_date = models.DateField(verbose_name="交易日期")
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="金额"
    )

    class Meta:
        verbose_name = "出入金记录"
        verbose_name_plural = "出入金记录"
        ordering = ['-transaction_date']
        indexes = [
            models.Index(fields=['user', '-transaction_date']),
        ]

    def __str__(self) -> str:
        transaction_type = "入金" if self.amount >= 0 else "出金"
        amount_abs = abs(self.amount)
        return f"{self.user.username} - {transaction_type} {amount_abs} ({self.transaction_date})"
