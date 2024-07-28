from django.db import models
from datetime import date

class Video(models.Model):
    created_at = models.DateField(default=date.today)
    title = models.CharField(max_length=100)
    description = models.TextField()
    thumbnails = models.ImageField(upload_to='thumbnails/', null=True, blank=True)
    video_360p_m3u8 = models.FileField(upload_to='videos/', null=True, blank=True)
    video_720p_m3u8 = models.FileField(upload_to='videos/', null=True, blank=True)
    video_1080p_m3u8 = models.FileField(upload_to='videos/', null=True, blank=True)
    video_master_m3u8 = models.FileField(upload_to='videos/', null=True, blank=True)
    video_file = models.FileField(upload_to='videos/', null=True, blank=True)
    genre = models.CharField(max_length=100, null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)