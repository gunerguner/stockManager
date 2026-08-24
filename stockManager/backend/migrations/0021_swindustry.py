import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0020_seed_sw_l1_tags"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Tag",
            new_name="SwIndustry",
        ),
        migrations.RemoveConstraint(
            model_name="swindustry",
            name="uniq_tag_category_code",
        ),
        migrations.RemoveField(
            model_name="swindustry",
            name="category",
        ),
        migrations.AlterField(
            model_name="swindustry",
            name="code",
            field=models.CharField(max_length=16, verbose_name="行业代码"),
        ),
        migrations.AlterField(
            model_name="swindustry",
            name="name",
            field=models.CharField(max_length=64, verbose_name="行业名称"),
        ),
        migrations.AddConstraint(
            model_name="swindustry",
            constraint=models.UniqueConstraint(
                fields=("code",),
                name="uniq_swindustry_code",
            ),
        ),
        migrations.AlterModelOptions(
            name="swindustry",
            options={"verbose_name": "申万行业", "verbose_name_plural": "申万行业"},
        ),
        migrations.RenameField(
            model_name="stockmeta",
            old_name="tag",
            new_name="swIndustry",
        ),
        migrations.AlterField(
            model_name="stockmeta",
            name="swIndustry",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="stocks",
                to="backend.swindustry",
                verbose_name="申万行业",
            ),
        ),
    ]
