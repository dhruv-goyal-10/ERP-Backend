# Generated by Django 4.1.2 on 2022-11-02 18:21

import datetime
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0012_alter_user_otp_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='mother_name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='student',
            name='mother_phone',
            field=models.BigIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1000000000), django.core.validators.MaxValueValidator(9999999999)]),
        ),
        migrations.AlterField(
            model_name='user',
            name='otp_created_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 2, 18, 20, 9, 834879, tzinfo=datetime.timezone.utc)),
        ),
    ]
