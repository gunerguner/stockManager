from django.db import migrations, models


def backfill_sort_order(apps, schema_editor):
    Operation = apps.get_model('backend', 'Operation')
    ops = Operation.objects.all().order_by('user_id', 'code', 'date', 'id')
    current_key = None
    sort_index = 0
    updates = []
    for op in ops.iterator():
        key = (op.user_id, op.code, op.date)
        if key != current_key:
            current_key = key
            sort_index = 0
        op.sortOrder = sort_index
        sort_index += 1
        updates.append(op)
    if updates:
        Operation.objects.bulk_update(updates, ['sortOrder'], batch_size=500)


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0008_stockmeta_name_stockmeta_nameupdatedat'),
    ]

    operations = [
        migrations.AddField(
            model_name='operation',
            name='sortOrder',
            field=models.PositiveIntegerField(default=0, verbose_name='同日顺序'),
        ),
        migrations.RunPython(backfill_sort_order, migrations.RunPython.noop),
    ]
