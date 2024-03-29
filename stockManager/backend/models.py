import datetime
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.utils import timezone

# Create your models here.


class Operation(models.Model):
    class operationType(models.TextChoices):
        BUY = "BUY", _("买入")
        SELL = "SELL", _("卖出")
        Divident = "DV", _("除权除息")

    code = models.CharField(max_length=200)
    date = models.DateField()
    operationType = models.CharField(
        max_length=4, choices=operationType.choices, default=operationType.BUY
    )
    price = models.FloatField(default=0)
    count = models.IntegerField(default=0, blank=True)
    fee = models.FloatField(default=0)
    comment = models.CharField(max_length=200, blank=True)
    cash = models.FloatField(default=0)  # 分红
    stock = models.FloatField(default=0)  # 送股
    reserve = models.FloatField(default=0)  # 派股

    def __str__(self):
        return (
            self.code
            + " "
            + str(self.date)
            + " "
            + self.operationType
            + " "
            + str(self.count)
        )

    def to_dict(self):
        to_return = {}
        to_return["date"] = str(self.date)
        to_return["type"] = self.operationType
        to_return["price"] = self.price
        to_return["count"] = self.count
        to_return["fee"] = self.fee
        if self.operationType == "BUY" or self.operationType == "SELL":
            to_return["sum"] = self.price * self.count
        elif self.operationType == "DV":
            to_return["sum"] = self.cash * self.count

        if self.operationType == "DV":
            comment = ""
            if self.cash > 0.0:
                comment += "每10股股息" + "%.2f" % (self.cash * 10)
            if self.reserve > 0.0:
                comment += ",每10股转增" + "%.2f" % (self.reserve * 10)
            if self.stock > 0.0:
                comment += ",每10股送股" + "%.2f" % (self.stock * 10)

            to_return["comment"] = comment
        return to_return


class Info(models.Model):
    key = models.CharField(max_length=200)
    value = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.key + " : " + self.value


class StockMeta(models.Model):
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

    code = models.CharField(max_length=200)
    isNew = models.BooleanField(default=False)
    stockType = models.CharField(
        max_length=6, choices=stockType.choices, default=stockType.OTHER
    )

    def __str__(self):
        return self.code + "  " + self.stockType