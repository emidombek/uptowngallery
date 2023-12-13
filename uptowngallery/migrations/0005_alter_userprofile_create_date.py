# Generated by Django 4.2 on 2023-12-13 15:28

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('uptowngallery', '0004_alter_artwork_create_date_alter_auction_create_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='create_date',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text='The date when the user profile was created.', verbose_name='Create Date'),
        ),
    ]
