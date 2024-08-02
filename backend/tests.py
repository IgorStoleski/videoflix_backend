from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Video
from .serializer import VideoViewSerializer
from unittest.mock import patch, MagicMock, mock_open

import os
import subprocess
import unittest
from django.core.files import File
from django.conf import settings
from backend.models import Video
from backend.tasks import (
    convert_360p, convert_720p, convert_1080p, generate_thumbnail,
    save_thumbnail_to_model, run_command, convert_hls, save_to_model, create_master_playlist
)
from backend.signals import video_post_save, auto_delete_file_on_delete

class VideoAPITests(APITestCase):

    def setUp(self):
        self.video = Video.objects.create(title="Test Video", genre="Action", description="Action video")

    def test_video_create(self):
        url = reverse('video-list')
        data = {'title': 'New Video', 'genre': 'Action', 'description': 'New action video'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Video.objects.count(), 2)

    def test_video_update(self):
        url = reverse('video-detail', args=[self.video.id])
        data = {'title': 'Updated Video', 'genre': 'Action', 'description': 'Updated action video'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.video.refresh_from_db()
        self.assertEqual(self.video.title, 'Updated Video')

    def test_video_delete(self):
        url = reverse('video-detail', args=[self.video.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Video.objects.count(), 0)

    def test_video_by_genre_list(self):
        response = self.client.get(reverse('video-by-genre', args=['Action']))
        videos = Video.objects.filter(genre='Action')
        serializer = VideoViewSerializer(videos, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_video_by_genre_list_not_found(self):
        response = self.client.get(reverse('video-by-genre', args=['NonExistentGenre']))
        videos = Video.objects.filter(genre='NonExistentGenre')
        serializer = VideoViewSerializer(videos, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)


class VideoSignalsTests(TestCase):

    @patch('backend.tasks.generate_thumbnail')
    @patch('backend.tasks.save_thumbnail_to_model')
    @patch('django_rq.get_queue')
    def test_video_post_save_created(self, mock_get_queue, mock_save_thumbnail_to_model, mock_generate_thumbnail):
        mock_queue = MagicMock()
        mock_get_queue.return_value = mock_queue
        mock_generate_thumbnail.return_value = 'thumbnail.png'

        video = Video.objects.create(title='Test Video', video_file='testlocation/video.mp4')

        video_post_save(Video, video, created=True)

        mock_generate_thumbnail.assert_called_once_with('testlocation/video.mp4', 'testlocation/video_thumbnail.png')
        mock_save_thumbnail_to_model.assert_called_once_with(video.id, 'thumbnail.png')
        self.assertEqual(mock_queue.enqueue.call_count, 3)

    @patch('backend.tasks.generate_thumbnail')
    @patch('backend.tasks.save_thumbnail_to_model')
    @patch('django_rq.get_queue')
    def test_video_post_save_not_created(self, mock_get_queue, mock_save_thumbnail_to_model, mock_generate_thumbnail):
        mock_queue = MagicMock()
        mock_get_queue.return_value = mock_queue

        video = Video.objects.create(title='Test Video', video_file='testlocation/video.mp4')

        video_post_save(Video, video, created=False)

        mock_generate_thumbnail.assert_not_called()
        mock_save_thumbnail_to_model.assert_not_called()
        mock_queue.enqueue.assert_not_called()

    @patch('os.path.isfile', return_value=True)
    @patch('os.remove')
    def test_auto_delete_file_on_delete(self, mock_remove, mock_isfile):
        video = Video.objects.create(title='Test Video', video_file='testlocation/video.mp4')

        auto_delete_file_on_delete(Video, video)

        mock_isfile.assert_called_once_with('testlocation/video.mp4')
        mock_remove.assert_called_once_with('testlocation/video.mp4')

    @patch('os.path.isfile', return_value=False)
    @patch('os.remove')
    def test_auto_delete_file_on_delete_file_not_exists(self, mock_remove, mock_isfile):
        video = Video.objects.create(title='Test Video', video_file='testlocation/video.mp4')

        auto_delete_file_on_delete(Video, video)

        mock_isfile.assert_called_once_with('testlocation/video.mp4')
        mock_remove.assert_not_called()


class VideoProcessingTests(unittest.TestCase):

    @patch('subprocess.run')
    def test_run_command_success(self, mock_run):
        mock_run.return_value = MagicMock(stdout=b'output', stderr=b'')
        run_command('echo "Hello, World!"')
        mock_run.assert_called_once_with('echo "Hello, World!"', capture_output=True, shell=True, check=True)

    @patch('subprocess.run')
    def test_run_command_failure(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, 'cmd', stderr=b'error')
        with patch('builtins.print') as mock_print:
            run_command('invalid_command')
            mock_print.assert_called_with('Error: error')

    @patch('os.path.exists', return_value=True)
    @patch('backend.tasks.run_command')
    def test_generate_thumbnail_success(self, mock_run_command, mock_exists):
        thumbnail = generate_thumbnail('video.mp4', 'thumbnail.jpg')
        self.assertEqual(thumbnail, 'thumbnail.jpg')
        mock_run_command.assert_called_once()
        mock_exists.assert_called_once_with('thumbnail.jpg')

    @patch('os.path.exists', return_value=False)
    @patch('backend.tasks.run_command')
    def test_generate_thumbnail_failure(self, mock_run_command, mock_exists):
        thumbnail = generate_thumbnail('video.mp4', 'thumbnail.jpg')
        self.assertIsNone(thumbnail)
        mock_run_command.assert_called_once()
        mock_exists.assert_called_once_with('thumbnail.jpg')

    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    @patch('django.core.files.File')
    def test_save_thumbnail_to_model(self, mock_file, mock_open):
        video = Video.objects.create(title='Test Video')
        save_thumbnail_to_model(video.id, 'thumbnail.jpg')
        mock_open.assert_called_once_with('thumbnail.jpg', 'rb')
        mock_file.assert_called_once()

    @patch('os.path.exists', return_value=True)
    @patch('backend.tasks.convert_hls')
    @patch('backend.tasks.run_command')
    def test_convert_360p_success(self, mock_run_command, mock_convert_hls, mock_exists):
        convert_360p('video.mp4', 1)
        mock_run_command.assert_called_once()
        mock_convert_hls.assert_called_once_with('video_360p.mp4', '360p', 1)
        mock_exists.assert_called_once_with('video_360p.mp4')

    @patch('os.path.exists', return_value=False)
    @patch('backend.tasks.run_command')
    def test_convert_360p_failure(self, mock_run_command, mock_exists):
        with patch('builtins.print') as mock_print:
            convert_360p('video.mp4', 1)
            mock_run_command.assert_called_once()
            mock_exists.assert_called_once_with('video_360p.mp4')
            mock_print.assert_called_with('Fehler: 360p Datei video_360p.mp4 wurde nicht erstellt.')

    @patch('os.path.exists', return_value=True)
    @patch('backend.tasks.convert_hls')
    @patch('backend.tasks.run_command')
    def test_convert_720p_success(self, mock_run_command, mock_convert_hls, mock_exists):
        convert_720p('video.mp4', 1)
        mock_run_command.assert_called_once()
        mock_convert_hls.assert_called_once_with('video_720p.mp4', '720p', 1)
        mock_exists.assert_called_once_with('video_720p.mp4')

    @patch('os.path.exists', return_value=False)
    @patch('backend.tasks.run_command')
    def test_convert_720p_failure(self, mock_run_command, mock_exists):
        with patch('builtins.print') as mock_print:
            convert_720p('video.mp4', 1)
            mock_run_command.assert_called_once()
            mock_exists.assert_called_once_with('video_720p.mp4')
            mock_print.assert_called_with('Fehler: 720p Datei video_720p.mp4 wurde nicht erstellt.')

    @patch('os.path.exists', return_value=True)
    @patch('backend.tasks.convert_hls')
    @patch('backend.tasks.run_command')
    def test_convert_1080p_success(self, mock_run_command, mock_convert_hls, mock_exists):
        convert_1080p('video.mp4', 1)
        mock_run_command.assert_called_once()
        mock_convert_hls.assert_called_once_with('video_1080p.mp4', '1080p', 1)
        mock_exists.assert_called_once_with('video_1080p.mp4')

    @patch('os.path.exists', return_value=False)
    @patch('backend.tasks.run_command')
    def test_convert_1080p_failure(self, mock_run_command, mock_exists):
        with patch('builtins.print') as mock_print:
            convert_1080p('video.mp4', 1)
            mock_run_command.assert_called_once()
            mock_exists.assert_called_once_with('video_1080p.mp4')
            mock_print.assert_called_with('Fehler: 1080p Datei video_1080p.mp4 wurde nicht erstellt.')

    @patch('os.path.exists', return_value=True)
    @patch('backend.tasks.save_to_model')
    @patch('backend.tasks.run_command')
    def test_convert_hls_success(self, mock_run_command, mock_save_to_model, mock_exists):
        convert_hls('video.mp4', '360p', 1)
        mock_run_command.assert_called_once()
        mock_save_to_model.assert_called_once_with(1, 'video.m3u8', '360p')
        mock_exists.assert_called_once_with('video.m3u8')

    @patch('os.path.exists', return_value=False)
    @patch('backend.tasks.run_command')
    def test_convert_hls_failure(self, mock_run_command, mock_exists):
        with patch('builtins.print') as mock_print:
            convert_hls('video.mp4', '360p', 1)
            mock_run_command.assert_called_once()
            mock_exists.assert_called_once_with('video.m3u8')
            mock_print.assert_called_with('Fehler: HLS-Datei video.m3u8 wurde nicht erstellt.')

    @patch('backend.tasks.create_master_playlist')
    def test_save_to_model(self, mock_create_master_playlist):
        video = Video.objects.create(title='Test Video')
        with patch('os.path.relpath', return_value='testlocation/video.m3u8'):
            save_to_model(video.id, 'testlocation/video.m3u8', '360p')
            video.refresh_from_db()
            self.assertEqual(video.video_360p_m3u8, 'testlocation/video.m3u8')
            mock_create_master_playlist.assert_not_called()

    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists', return_value=True)
    def test_create_master_playlist(self, mock_exists, mock_open):
        video = Video.objects.create(
            title='Test Video',
            video_file='testlocation/video.mp4',
            video_360p_m3u8='testlocation/video_360p.m3u8',
            video_720p_m3u8='testlocation/video_720p.m3u8',
            video_1080p_m3u8='testlocation/video_1080p.m3u8'
        )

        create_master_playlist(video)

        # Ensure the file was opened for writing the master playlist
        mock_open.assert_called_with('testlocation/video_master.m3u8', 'w')
        handle = mock_open()
        handle.write.assert_any_call('#EXTM3U\n')
        handle.write.assert_any_call('#EXT-X-STREAM-INF:BANDWIDTH=800000,RESOLUTION=640x360\n')
        handle.write.assert_any_call('../testlocation/video_360p.m3u8\n')
        handle.write.assert_any_call('#EXT-X-STREAM-INF:BANDWIDTH=2800000,RESOLUTION=1280x720\n')
        handle.write.assert_any_call('../testlocation/video_720p.m3u8\n')
        handle.write.assert_any_call('#EXT-X-STREAM-INF:BANDWIDTH=5000000,RESOLUTION=1920x1080\n')
        handle.write.assert_any_call('../testlocation/video_1080p.m3u8\n')
        self.assertEqual(handle.write.call_count, 7)