# Generated by Django 3.2.22 on 2023-11-18 17:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('uptowngallery', '0002_artwork_auction_start'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='artwork',
            options={'ordering': ['-create_date']},
        ),
    ]
