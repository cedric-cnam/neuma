# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-10 11:49
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0030_auto_20170509_1623'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='corpus',
            options={'permissions': (('view_corpus', 'View corpus'),)},
        ),
    ]
