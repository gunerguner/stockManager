from django.db import models


class StockDailyPrice(models.Model):
    """股票日频不复权收盘价（全局共享，供净值回放）"""

    code = models.CharField(max_length=200, verbose_name="股票代码")
    date = models.DateField(verbose_name="交易日期")
    close = models.FloatField(verbose_name="收盘价")

    class Meta:
        verbose_name = "日频收盘价"
        verbose_name_plural = "日频收盘价"
        constraints = [
            models.UniqueConstraint(fields=['code', 'date'], name='uniq_stock_daily_price_code_date'),
        ]
        indexes = [
            models.Index(fields=['code', 'date']),
        ]
        ordering = ['code', 'date']

    def __str__(self) -> str:
        return f"{self.code} {self.date} {self.close}"


class HkdCnyDailyRate(models.Model):
    """HKD/CNY 日频汇率（中行牌价换算为 1 HKD = X CNY，全局共享）"""

    date = models.DateField(verbose_name="日期", unique=True)
    close = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        verbose_name="汇率",
        help_text="1 HKD = X CNY",
    )

    class Meta:
        verbose_name = "港币日频汇率"
        verbose_name_plural = "港币日频汇率"
        ordering = ["date"]

    def __str__(self) -> str:
        return f"{self.date} {self.close}"
