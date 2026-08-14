from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0017_operation_money_decimal'),
    ]

    operations = [
        migrations.CreateModel(
            name='HkdCnyDailyRate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(unique=True, verbose_name='日期')),
                ('close', models.DecimalField(
                    decimal_places=6,
                    help_text='1 HKD = X CNY',
                    max_digits=10,
                    verbose_name='汇率',
                )),
            ],
            options={
                'verbose_name': '港币日频汇率',
                'verbose_name_plural': '港币日频汇率',
                'ordering': ['date'],
            },
        ),
    ]
