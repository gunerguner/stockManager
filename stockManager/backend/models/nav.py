from django.contrib.auth.models import User
from django.db import models


class PortfolioNavDaily(models.Model):
    """用户组合日净值（库内不含 incomeCash）"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='portfolio_nav_dailies',
        verbose_name="用户",
    )
    date = models.DateField(verbose_name="交易日期")
    nav = models.FloatField(verbose_name="净值")
    units = models.FloatField(default=0, verbose_name="份额")
    asset = models.FloatField(default=0, verbose_name="总资产")
    cash = models.FloatField(default=0, verbose_name="现金")

    class Meta:
        verbose_name = "组合日净值"
        verbose_name_plural = "组合日净值"
        constraints = [
            models.UniqueConstraint(fields=['user', 'date'], name='uniq_portfolio_nav_user_date'),
        ]
        indexes = [
            models.Index(fields=['user', 'date']),
        ]
        ordering = ['user', 'date']

    def __str__(self) -> str:
        return f"{self.user.username} {self.date} nav={self.nav}"
