# Generated by Django 4.2 on 2024-03-04 12:41

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('uptowngallery', '0009_alter_bids_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='artwork',
            name='image',
            field=cloudinary.models.CloudinaryField(default='https://res.cloudinary.com/dh4ck00n3/image/upload/v1700227378/comic-cartoon-speech-bubble-wow-emotions-yellow-backdrop_dlgmhv.jpg', max_length=255, verbose_name='Image'),
            preserve_default=False,
        ),
    ]