# Generated by Django 3.2.22 on 2023-11-18 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('uptowngallery', '0003_alter_artwork_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='artwork',
            name='approval_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved')], default='pending', max_length=20, verbose_name='Approval Status'),
        ),
    ]
