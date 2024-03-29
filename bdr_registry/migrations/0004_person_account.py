# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-07-01 13:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("bdr_registry", "0003_auto_20200403_1007"),
    ]

    operations = [
        migrations.AddField(
            model_name="person",
            name="account",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="person",
                to="bdr_registry.Account",
            ),
        ),
    ]
