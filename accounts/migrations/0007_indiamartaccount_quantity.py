# Generated by Django 3.2.14 on 2024-10-19 04:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_remove_categorykeyword_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='indiamartaccount',
            name='quantity',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
