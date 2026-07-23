# Generated manually for Operation/WatchItem -> StockMeta FK

from django.db import migrations, models
import django.db.models.deletion


def _infer_stock_type(code: str) -> str:
    if code.startswith('hk'):
        return 'HK'
    if code.startswith('sh600') or code.startswith('sh601') or code.startswith('sh603') or code.startswith('sh605'):
        return 'SH60'
    if code.startswith('sh688'):
        return 'SH688'
    if code.startswith('sz300') or code.startswith('sz301'):
        return 'SZ300'
    if code.startswith('sz000') or code.startswith('sz001') or code.startswith('sz002') or code.startswith('sz003'):
        return 'SZ00'
    if code.startswith('bj'):
        return 'BJ'
    return 'OTHER'


def backfill_stock_meta(apps, schema_editor):
    StockMeta = apps.get_model('backend', 'StockMeta')
    Operation = apps.get_model('backend', 'Operation')
    WatchItem = apps.get_model('backend', 'WatchItem')

    code_to_id = {meta.code: meta.id for meta in StockMeta.objects.all()}

    def resolve_meta_id(code: str) -> int:
        meta_id = code_to_id.get(code)
        if meta_id is not None:
            return meta_id
        meta = StockMeta.objects.create(
            code=code,
            name='',
            stockType=_infer_stock_type(code),
            isNew=False,
        )
        code_to_id[code] = meta.id
        return meta.id

    ops = list(Operation.objects.all())
    for op in ops:
        op.stock_meta_id = resolve_meta_id(op.code)
    if ops:
        Operation.objects.bulk_update(ops, ['stock_meta_id'], batch_size=500)

    items = list(WatchItem.objects.all())
    for item in items:
        item.stock_meta_id = resolve_meta_id(item.code)
    if items:
        WatchItem.objects.bulk_update(items, ['stock_meta_id'], batch_size=500)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0013_watchitem_hidden'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockmeta',
            name='code',
            field=models.CharField(max_length=200, unique=True, verbose_name='股票代码'),
        ),
        migrations.AddField(
            model_name='operation',
            name='stock_meta',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='operations',
                to='backend.stockmeta',
                verbose_name='股票',
            ),
        ),
        migrations.AddField(
            model_name='watchitem',
            name='stock_meta',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='watch_items',
                to='backend.stockmeta',
                verbose_name='股票',
            ),
        ),
        migrations.RunPython(backfill_stock_meta, noop_reverse),
        migrations.AlterField(
            model_name='operation',
            name='stock_meta',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='operations',
                to='backend.stockmeta',
                verbose_name='股票',
            ),
        ),
        migrations.AlterField(
            model_name='watchitem',
            name='stock_meta',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='watch_items',
                to='backend.stockmeta',
                verbose_name='股票',
            ),
        ),
        migrations.AlterUniqueTogether(
            name='watchitem',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='watchitem',
            constraint=models.UniqueConstraint(
                fields=('user', 'stock_meta'),
                name='uniq_watchitem_user_stock_meta',
            ),
        ),
        migrations.RemoveField(
            model_name='operation',
            name='code',
        ),
        migrations.RemoveField(
            model_name='watchitem',
            name='code',
        ),
    ]
