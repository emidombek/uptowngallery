# Generated by Django 4.2.7 on 2023-11-27 12:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('uptowngallery', '0005_alter_artwork_approval_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='name',
            field=models.CharField(help_text='The name of the user.', max_length=255, null=True, verbose_name='Name'),
        ),
    ]
