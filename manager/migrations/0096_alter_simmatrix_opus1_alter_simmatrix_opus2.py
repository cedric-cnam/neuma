# Generated by Django 4.2 on 2023-06-30 15:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("manager", "0095_opus_composer_ld"),
    ]

    operations = [
        migrations.AlterField(
            model_name="simmatrix",
            name="opus1",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="%(app_label)s_%(class)s_opus1",
                to="manager.opus",
            ),
        ),
        migrations.AlterField(
            model_name="simmatrix",
            name="opus2",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="%(app_label)s_%(class)s_opus2",
                to="manager.opus",
            ),
        ),
    ]
