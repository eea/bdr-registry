# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-07-10 08:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bdr_registry', '0004_person_account'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='is_main_user',
            field=models.BooleanField(default=False),
        ),
    ]