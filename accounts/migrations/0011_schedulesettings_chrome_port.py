# Generated by Django 5.1.2 on 2024-11-03 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_profile_stop_selenium'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedulesettings',
            name='chrome_port',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
