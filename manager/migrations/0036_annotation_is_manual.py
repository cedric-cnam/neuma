# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-11-13 17:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0035_opus_record'),
    ]

    operations = [
        migrations.AddField(
            model_name='annotation',
            name='is_manual',
            field=models.BooleanField(default=False),
        ),
    ]
