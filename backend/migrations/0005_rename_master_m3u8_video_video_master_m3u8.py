# Generated by Django 5.0.6 on 2024-07-02 16:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0004_video_master_m3u8'),
    ]

    operations = [
        migrations.RenameField(
            model_name='video',
            old_name='master_m3u8',
            new_name='video_master_m3u8',
        ),
    ]
