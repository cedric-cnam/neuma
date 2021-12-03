# Generated by Django 3.2.5 on 2021-12-03 16:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transcription', '0015_auto_20210210_1106'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grammar',
            name='type_weight',
            field=models.CharField(choices=[('proba', 'Probability'), ('penalty', 'Penalty')], default='proba', max_length=30),
        ),
    ]
