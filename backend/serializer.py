from rest_framework import serializers
from .models import Video

class VideoViewSerializer(serializers.ModelSerializer):
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