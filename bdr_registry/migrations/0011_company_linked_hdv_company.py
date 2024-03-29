# Generated by Django 3.2.4 on 2023-06-01 10:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("bdr_registry", "0010_auto_20230601_1057"),
    ]

    operations = [
        migrations.AddField(
            model_name="company",
            name="linked_hdv_company",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="bdr_registry.company",
            ),
        ),
    ]
