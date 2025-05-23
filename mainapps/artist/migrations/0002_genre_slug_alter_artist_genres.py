# Generated by Django 5.1.7 on 2025-04-01 04:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('artist', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='genre',
            name='slug',
            field=models.SlugField(blank=True, editable=False, max_length=70, unique=True),
        ),
        migrations.AlterField(
            model_name='artist',
            name='genres',
            field=models.ManyToManyField(blank=True, related_name='artists', to='artist.genre'),
        ),
    ]
