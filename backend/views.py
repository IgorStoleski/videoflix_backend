
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from rest_framework import generics
from .models import Video
from .serializer import VideoViewSerializer


CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

class VideoList(generics.ListAPIView):
    """
    API view to retrieve a list of videos.
    This view lists all videos available in the database, serialized by `VideoViewSerializer`.    
    Attributes:
        queryset (QuerySet): The set of all `Video` objects.
        serializer_class (VideoViewSerializer): The serializer class for video objects.
    """
    queryset = Video.objects.all()
    serializer_class = VideoViewSerializer


class VideoDetail(generics.RetrieveAPIView):
    """
    API view to retrieve a detailed view of a specific video.
    This view provides detailed information about a video identified by its ID, using the `VideoViewSerializer`.    
    Attributes:
        queryset (QuerySet): The set of all `Video` objects.
        serializer_class (VideoViewSerializer): The serializer class for video objects.
    """
    queryset = Video.objects.all()
    serializer_class = VideoViewSerializer


class VideoByGenreList(generics.ListAPIView):
    """
    API view to retrieve a list of videos filtered by genre.
    This view returns a list of videos that match a specific genre, which is provided via the URL.    
    Attributes:
        serializer_class (VideoViewSerializer): The serializer class for video objects.    
    Methods:
        get_queryset(self): Filters the `Video` objects by the genre specified in the URL.
    """
    serializer_class = VideoViewSerializer

    def get_queryset(self):
        """
        Filter the video queryset based on the genre provided in the URL.        
        Returns:
            QuerySet: A queryset of `Video` objects filtered by the specified genre.
        """
        genre = self.kwargs['genre']
        return Video.objects.filter(genre=genre)

