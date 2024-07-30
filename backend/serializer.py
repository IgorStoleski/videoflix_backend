from rest_framework import serializers
from .models import Video

class VideoViewSerializer(serializers.ModelSerializer):
    """
    Serializer for viewing video details.
    This serializer provides a comprehensive representation of a Video object, suitable for API responses. It serializes video metadata along with various video stream qualities and thumbnails for a rich client-side integration.
    Attributes:
        id (int): Unique identifier of the video.
        created_at (datetime): Timestamp when the video was created.
        title (str): Title of the video.
        description (str): Description or summary of the video content.
        thumbnails (list): List of URLs pointing to thumbnail images of varying resolutions.
        video_360p_m3u8 (str): URL to the 360p quality HLS stream of the video.
        video_720p_m3u8 (str): URL to the 720p quality HLS stream of the video.
        video_1080p_m3u8 (str): URL to the 1080p quality HLS stream of the video.
        video_master_m3u8 (str): URL to the master playlist HLS stream, which includes all available qualities.
        video_file (FileField): Direct link to the video file, typically for download purposes.
        genre (str): Genre of the video, helping in categorization.
    Meta:
        model (Model): The database model representing Videos.
        fields (list): List of fields from the Video model that are included in the serialization.
    """
    class Meta:
        model = Video
        fields = [
            'id',
            'created_at',
            'title',
            'description',
            'thumbnails',
            'video_360p_m3u8',
            'video_720p_m3u8',
            'video_1080p_m3u8',
            'video_master_m3u8',
            'video_file',
            'genre'
        ]