# Generated by Django 2.2.16 on 2022-07-19 08:14

import django.core.validators
from django.db import migrations, models
import users.validators


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20220716_2024'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=254, unique=True, validators=[django.core.validators.EmailValidator()], verbose_name='Электронная почта'),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=150, unique=True, validators=[users.validators.yamdb_username_validator], verbose_name='Имя пользователя'),
        ),
    ]