# Generated by Django 5.1.7 on 2025-03-19 18:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('directory', '0007_alter_ordertable_table_delete_table'),
    ]

    operations = [
        migrations.CreateModel(
            name='Table',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Стол', max_length=100, verbose_name='Стол')),
            ],
            options={
                'verbose_name': 'Стол',
            },
        ),
        migrations.AlterField(
            model_name='ordertable',
            name='table',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, to='directory.table'),
        ),
    ]
