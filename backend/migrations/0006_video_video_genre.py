# Generated by Django 5.0.6 on 2024-07-12 18:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0005_rename_master_m3u8_video_video_master_m3u8'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='video_genre',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
