# Generated by Django 3.2.22 on 2023-11-15 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('uptowngallery', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='artwork',
            name='auction_start',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
