# Generated by Django 5.0.6 on 2024-05-21 18:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='video_file',
            field=models.FileField(blank=True, null=True, upload_to='videos'),
        ),
    ]
