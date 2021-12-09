# Generated by Django 3.2.5 on 2021-12-08 22:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0058_alter_corpus_parent'),
    ]

    operations = [
        migrations.CreateModel(
            name='Licence',
            fields=[
                ('code', models.CharField(max_length=25, primary_key=True, serialize=False)),
                ('url', models.CharField(blank=True, max_length=25, null=True)),
                ('notice', models.TextField()),
                ('full_text', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'Licence',
            },
        ),
    ]
