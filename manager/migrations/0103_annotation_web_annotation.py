# Generated by Django 4.2 on 2024-06-12 15:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("manager", "0102_alter_opussource_source_file"),
    ]

    operations = [
        migrations.AddField(
            model_name="annotation",
            name="web_annotation",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
