# Generated by Django 2.2.16 on 2022-07-18 20:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='titles',
            name='year',
            field=models.IntegerField(help_text='Укажите год выпуска', verbose_name='Год выпуска'),
        ),
    ]