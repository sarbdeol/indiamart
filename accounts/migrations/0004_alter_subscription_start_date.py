# Generated by Django 3.2.14 on 2024-10-15 12:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_subscription'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='start_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
