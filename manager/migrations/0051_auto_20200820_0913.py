# Generated by Django 2.2.13 on 2020-08-20 09:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0050_opusmeta'),
    ]

    operations = [
        migrations.AlterField(
            model_name='opusmeta',
            name='meta_value',
            field=models.TextField(),
        ),
    ]
