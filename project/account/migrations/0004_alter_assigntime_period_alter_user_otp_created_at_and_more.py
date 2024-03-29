# Generated by Django 4.1.2 on 2022-11-08 12:34

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_rename_pic_teacher_picture_teacher_address_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assigntime',
            name='period',
            field=models.CharField(choices=[('8:30 - 9:20', '8:30 - 9:20'), ('9:20 - 10:10', '9:20 - 10:10'), ('11:00 - 11:50', '11:00 - 11:50'), ('11:50 - 12:40', '11:50 - 12:40'), ('1:30 - 2:20', '1:30 - 2:20')], default='11:00 - 11:50', max_length=50),
        ),
        migrations.AlterField(
            model_name='user',
            name='otp_created_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 8, 12, 33, 1, 403267, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterUniqueTogether(
            name='assignclass',
            unique_together={('subject', 'class_id')},
        ),
    ]
