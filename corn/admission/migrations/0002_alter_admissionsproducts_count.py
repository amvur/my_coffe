# Generated by Django 5.1.7 on 2025-03-22 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admission', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='admissionsproducts',
            name='count',
            field=models.IntegerField(verbose_name='Количество'),
        ),
    ]
