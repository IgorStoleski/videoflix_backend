import subprocess
import os
from django.conf import settings
from django.core.files import File
from .models import Video


def run_command(cmd):
    try:
        result = subprocess.run(cmd, capture_output=True, shell=True, check=True)
        print(result.stdout.decode())
        print(result.stderr.decode())
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr.decode()}")

def generate_thumbnail(video_file, thumbnail_file):
    print(f"Generating thumbnail for {video_file}")
    cmd = f'ffmpeg -i "{video_file}" -ss 00:00:01.000 -vframes 1 "{thumbnail_file}"'
    run_command(cmd)
    if os.path.exists(thumbnail_file):
        return thumbnail_file
    else:
        print(f"Fehler: Thumbnail Datei {thumbnail_file} wurde nicht erstellt.")
        return None

def save_thumbnail_to_model(video_id, thumbnail_file):
    video = Video.objects.get(id=video_id)
    with open(thumbnail_file, 'rb') as f:
        video.thumbnails.save(os.path.basename(thumbnail_file), File(f), save=True)
    print(f"Thumbnail gespeichert: {thumbnail_file}")


def convert_360p(source, video_id):
    print(f"Converting {source} to 360p")
    target = source.replace('.mp4', '_360p.mp4')
    cmd = f'ffmpeg -i "{source}" -s 640x360 -c:v libx264 -crf 23 -c:a aac -strict -2 "{target}"'
    run_command(cmd)
    if os.path.exists(target):
        convert_hls(target, '360p', video_id)
    else:
        print(f"Fehler: 360p Datei {target} wurde nicht erstellt.")

def convert_720p(source, video_id):
    print(f"Converting {source} to 720p")
    target = source.replace('.mp4', '_720p.mp4')
    cmd = f'ffmpeg -i "{source}" -s hd720 -c:v libx264 -crf 23 -c:a aac -strict -2 "{target}"'
    run_command(cmd)
    if os.path.exists(target):
        convert_hls(target, '720p', video_id)
    else:
        print(f"Fehler: 720p Datei {target} wurde nicht erstellt.")

def convert_1080p(source, video_id):
    print(f"Converting {source} to 1080p")
    target = source.replace('.mp4', '_1080p.mp4')
    cmd = f'ffmpeg -i "{source}" -s hd1080 -c:v libx264 -crf 23 -c:a aac -strict -2 "{target}"'
    run_command(cmd)
    if os.path.exists(target):
        convert_hls(target, '1080p', video_id)
    else:
        print(f"Fehler: 1080p Datei {target} wurde nicht erstellt.")

def convert_hls(target, resolution, video_id):
    print(f"Converting {target} to HLS")
    hls_target = target.replace('.mp4', '.m3u8')
    cmd_hls = f'ffmpeg -i "{target}" -codec: copy -start_number 0 -hls_time 10 -hls_list_size 0 -f hls "{hls_target}"'
    run_command(cmd_hls)
    if os.path.exists(hls_target):
        save_to_model(video_id, hls_target, resolution)
    else:
        print(f"Fehler: HLS-Datei {hls_target} wurde nicht erstellt.")

def save_to_model(video_id, hls_target, resolution):
    print(f"Saving {resolution} HLS file {hls_target} to model")
    video = Video.objects.get(id=video_id)
    relative_path = os.path.relpath(hls_target, settings.MEDIA_ROOT)
    if resolution == '360p':
        video.video_360p_m3u8 = relative_path
    elif resolution == '720p':
        video.video_720p_m3u8 = relative_path
    elif resolution == '1080p':
        video.video_1080p_m3u8 = relative_path

    if video.video_360p_m3u8 and video.video_720p_m3u8 and video.video_1080p_m3u8:
        create_master_playlist(video)

    video.save()
    print(f"{resolution} HLS-Datei gespeichert: {relative_path}")

def create_master_playlist(video):
    source = video.video_file.path
    master_playlist_path = source.replace('.mp4', '_master.m3u8')

    print(f"Erstelle Master-Playlist: {master_playlist_path}")

    with open(master_playlist_path, 'w') as f:
        f.write('#EXTM3U\n')

        if video.video_360p_m3u8:
            f.write('#EXT-X-STREAM-INF:BANDWIDTH=800000,RESOLUTION=640x360\n')
            f.write(f"../{video.video_360p_m3u8}\n")

        if video.video_720p_m3u8:
            f.write('#EXT-X-STREAM-INF:BANDWIDTH=2800000,RESOLUTION=1280x720\n')
            f.write(f"../{video.video_720p_m3u8}\n")

        if video.video_1080p_m3u8:
            f.write('#EXT-X-STREAM-INF:BANDWIDTH=5000000,RESOLUTION=1920x1080\n')
            f.write(f"../{video.video_1080p_m3u8}\n")

    if os.path.exists(master_playlist_path):
        relative_path = os.path.relpath(master_playlist_path, settings.MEDIA_ROOT)
        video.video_master_m3u8 = relative_path
        video.save()
        print(f"Master-Playlist gespeichert: {relative_path}")
    else:
        print(f"Fehler: Master-Playlist {master_playlist_path} wurde nicht erstellt.")
