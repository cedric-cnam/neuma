# Generated by Django 3.2.5 on 2021-12-04 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0054_alter_corpus_licence_notice'),
    ]

    operations = [
        migrations.AlterField(
            model_name='corpus',
            name='licence_notice',
            field=models.TextField(blank=True, default=''),
        ),
    ]
