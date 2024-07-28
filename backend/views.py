
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from rest_framework import generics
from .models import Video
from .serializer import VideoViewSerializer


CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

class VideoList(generics.ListAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoViewSerializer


class VideoDetail(generics.RetrieveAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoViewSerializer


class VideoByGenreList(generics.ListAPIView):
    serializer_class = VideoViewSerializer

    def get_queryset(self):
        genre = self.kwargs['genre']
        return Video.objects.filter(genre=genre)

