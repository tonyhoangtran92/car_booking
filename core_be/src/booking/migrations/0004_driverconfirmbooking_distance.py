# Generated by Django 3.2.13 on 2022-11-14 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0003_booking_allow_driver_distance'),
    ]

    operations = [
        migrations.AddField(
            model_name='driverconfirmbooking',
            name='distance',
            field=models.IntegerField(default=0),
        ),
    ]
