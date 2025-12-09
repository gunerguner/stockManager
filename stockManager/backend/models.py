from typing import Dict, Any
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _


class Operation(models.Model):
    """股票操作记录模型"""
    
    class operationType(models.TextChoices):
        BUY = "BUY", _("买入")
        SELL = "SELL", _("卖出")
        Divident = "DV", _("除权除息")

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='operations', verbose_name="用户")
    code = models.CharField(max_length=200, verbose_name="股票代码")
    date = models.DateField(verbose_name="交易日期")
    operationType = models.CharField(
        max_length=4, 
        choices=operationType.choices, 
        default=operationType.BUY,
        verbose_name="操作类型"
    )
    price = models.FloatField(default=0, verbose_name="价格")
    count = models.IntegerField(default=0, blank=True, verbose_name="数量")
    fee = models.FloatField(default=0, verbose_name="手续费")
    comment = models.CharField(max_length=200, blank=True, verbose_name="备注")
    cash = models.FloatField(default=0, verbose_name="分红")
    stock = models.FloatField(default=0, verbose_name="送股")
    reserve = models.FloatField(default=0, verbose_name="转增")

    class Meta:
        verbose_name = "股票操作记录"
        verbose_name_plural = "股票操作记录"

    def __str__(self) -> str:
        return f"{self.user.username} - {self.code} {self.date} {self.operationType} {self.count}"

    def to_dict(self) -> Dict[str, Any]:
        data = {}
        data["date"] = str(self.date)
        data["type"] = self.operationType
        data["price"] = self.price
        data["count"] = self.count
        data["fee"] = self.fee
        if self.operationType == "BUY" or self.operationType == "SELL":
            data["sum"] = self.price * self.count
        elif self.operationType == "DV":
            data["sum"] = self.cash * self.count

        if self.operationType == "DV":
            comment = ""
            if self.cash > 0.0:
                comment += "每10股股息" + "%.2f" % (self.cash * 10)
            if self.reserve > 0.0:
                comment += ",每10股转增" + "%.2f" % (self.reserve * 10)
            if self.stock > 0.0:
                comment += ",每10股送股" + "%.2f" % (self.stock * 10)

            data["comment"] = comment
        return data


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
        return f"{self.user.username} - {self.get_info_type_display()}: {self.value}"


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
        return f"{self.user.username} - {transaction_type} {abs(self.amount)} ({self.transaction_date})"


class StockMeta(models.Model):
    """股票元数据模型（全局共享）"""
    
    class stockType(models.TextChoices):
        SH60 = "SH60", _("沪市")
        SZ00 = "SZ00", _("深市")
        SZ300 = "SZ300", _("创业板")
        SH688 = "SH688", _("科创板")
        BJ = "BJ", _("北交所")
        CONV = "CONV", _("可转债")
        FUNDIN = "FUNDIN", _("场内基金")
        FUNDAB = "FUNDAB", _("分级基金")
        OTHER = "OTHER", _("其它")

    code = models.CharField(max_length=200, verbose_name="股票代码")
    isNew = models.BooleanField(default=False, verbose_name="是否新股")
    stockType = models.CharField(
        max_length=6, 
        choices=stockType.choices, 
        default=stockType.OTHER,
        verbose_name="股票类型"
    )

    class Meta:
        verbose_name = "股票元数据"
        verbose_name_plural = "股票元数据"

    def __str__(self) -> str:
        return f"{self.code} - {self.get_stockType_display()}"