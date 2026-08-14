# Generated manually for Operation money fields Float -> Decimal

from decimal import ROUND_HALF_UP, Decimal

from django.db import migrations, models

_PRICE_QUANT = Decimal("0.0001")
_MONEY_QUANT = Decimal("0.01")
_CASH_QUANT = Decimal("0.000001")


def _to_decimal(value) -> Decimal:
    if value is None:
        return Decimal("0")
    if isinstance(value, Decimal):
        return value
    if isinstance(value, float):
        return Decimal(str(value))
    if isinstance(value, int):
        return Decimal(value)
    text = str(value).strip()
    return Decimal(text) if text else Decimal("0")


def _quantize(value, quant: Decimal) -> Decimal:
    return _to_decimal(value).quantize(quant, rounding=ROUND_HALF_UP)


def _quantize_operation_money(apps, schema_editor):
    """AlterField 前先把 REAL 脏尾数收口到约定小数位。"""
    Operation = apps.get_model("backend", "Operation")
    to_update: list = []
    for op in Operation.objects.all().iterator():
        op.price = _quantize(op.price, _PRICE_QUANT)
        op.fee = _quantize(op.fee, _MONEY_QUANT)
        op.cash = _quantize(op.cash, _CASH_QUANT)
        if op.amount is not None:
            op.amount = _quantize(op.amount, _MONEY_QUANT)
        to_update.append(op)
        if len(to_update) >= 500:
            Operation.objects.bulk_update(
                to_update, ["price", "fee", "amount", "cash"]
            )
            to_update.clear()
    if to_update:
        Operation.objects.bulk_update(
            to_update, ["price", "fee", "amount", "cash"]
        )


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0016_portfolio_nav_and_daily_price"),
    ]

    operations = [
        migrations.RunPython(
            _quantize_operation_money,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="operation",
            name="price",
            field=models.DecimalField(
                decimal_places=4,
                default=Decimal("0"),
                max_digits=16,
                verbose_name="价格",
            ),
        ),
        migrations.AlterField(
            model_name="operation",
            name="fee",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("0"),
                max_digits=15,
                verbose_name="手续费",
            ),
        ),
        migrations.AlterField(
            model_name="operation",
            name="amount",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text="仅港股通买卖填写；非港股留空",
                max_digits=15,
                null=True,
                verbose_name="成交金额(人民币)",
            ),
        ),
        migrations.AlterField(
            model_name="operation",
            name="cash",
            field=models.DecimalField(
                decimal_places=6,
                default=Decimal("0"),
                max_digits=16,
                verbose_name="分红",
            ),
        ),
    ]
