# Generated by Django 5.1.7 on 2025-04-01 22:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0005_alter_bookinggroup_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='booking',
            name='user',
        ),
        migrations.RemoveField(
            model_name='bookinggroup',
            name='user',
        ),
    ]
