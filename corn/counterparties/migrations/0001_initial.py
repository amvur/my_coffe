# Generated by Django 5.1.7 on 2025-03-22 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Counterpartys',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Имя')),
                ('phone', models.IntegerField(blank=True, null=True, verbose_name='Телефон')),
                ('address', models.CharField(blank=True, max_length=100, null=True, verbose_name='Адрес')),
            ],
        ),
    ]
