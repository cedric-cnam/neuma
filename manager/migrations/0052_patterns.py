# Generated by Django 3.2.5 on 2021-12-03 16:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0051_auto_20200820_0913'),
    ]

    operations = [
        migrations.CreateModel(
            name='Patterns',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('part', models.CharField(max_length=30)),
                ('voice', models.CharField(max_length=30)),
                ('content_type', models.CharField(max_length=30)),
                ('value', models.TextField()),
                ('opus', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manager.opus')),
            ],
            options={
                'db_table': 'Patterns',
            },
        ),
    ]
