from django.db import models
from datetime import date

class Video(models.Model):
    """
    Represents a video record, containing details and various resolution streams.
    Attributes:
        created_at (models.DateField): The date when the video was created. Defaults to the current day.
        title (models.CharField): The title of the video, limited to 100 characters.
        description (models.TextField): A text field that describes the video.
        thumbnails (models.ImageField): An optional image field for storing video thumbnails. Stored in the 'thumbnails/' directory.
        video_360p_m3u8 (models.FileField): An optional field for storing the 360p .m3u8 video file. Stored in the 'videos/' directory.
        video_720p_m3u8 (models.FileField): An optional field for storing the 720p .m3u8 video file. Stored in the 'videos/' directory.
        video_1080p_m3u8 (models.FileField): An optional field for storing the 1080p .m3u8 video file. Stored in the 'videos/' directory.
        video_master_m3u8 (models.FileField): An optional field for storing the master .m3u8 video file. Stored in the 'videos/' directory.
        video_file (models.FileField): An optional field for storing a video file in any format. Stored in the 'videos/' directory.
        genre (models.CharField): An optional field describing the genre of the video, limited to 100 characters.
    Methods:
        save(*args, **kwargs): Saves the current instance. Overrides the default save method to perform additional actions.
    """
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