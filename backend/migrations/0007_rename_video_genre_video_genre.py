# Generated by Django 5.0.6 on 2024-07-12 18:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0006_video_video_genre'),
    ]

    operations = [
        migrations.RenameField(
            model_name='video',
            old_name='video_genre',
            new_name='genre',
        ),
    ]