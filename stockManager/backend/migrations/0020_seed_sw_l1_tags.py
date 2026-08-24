from pathlib import Path

import yaml
from django.db import migrations

_SW_INDUSTRY_YAML = Path(__file__).resolve().parent.parent / "models" / "sw_industry.yaml"


def seed_sw_l1_tags(apps, schema_editor):
    Tag = apps.get_model("backend", "Tag")
    payload = yaml.safe_load(_SW_INDUSTRY_YAML.read_text(encoding="utf-8"))
    category = payload.get("category", "sw_l1")
    rows = payload.get("industries") or payload.get("tags") or []
    for row in rows:
        Tag.objects.get_or_create(
            category=category,
            code=str(row["code"]),
            defaults={"name": row["name"]},
        )


def unseed_sw_l1_tags(apps, schema_editor):
    Tag = apps.get_model("backend", "Tag")
    Tag.objects.filter(category="sw_l1").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0019_tag_and_stockmeta_tag"),
    ]

    operations = [
        migrations.RunPython(seed_sw_l1_tags, unseed_sw_l1_tags),
    ]
