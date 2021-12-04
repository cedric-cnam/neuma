# Generated by Django 3.2.5 on 2021-12-04 13:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0058_alter_corpus_parent'),
        ('migration', '0002_corpusmigration_parent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='corpusmigration',
            name='corpus',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='manager.corpus'),
        ),
        migrations.AlterField(
            model_name='corpusmigration',
            name='parent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='migration.corpusmigration'),
        ),
        migrations.AlterField(
            model_name='opusmigration',
            name='opus',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='manager.opus'),
        ),
    ]
