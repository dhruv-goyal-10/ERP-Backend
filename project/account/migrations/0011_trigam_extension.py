from django.db import migrations, models
import django.db.models.deletion
from django.contrib.postgres.operations import TrigramExtension


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0010_alter_studentattendance_unique_together'),
    ]

    operations = [
        TrigramExtension(),
    ]