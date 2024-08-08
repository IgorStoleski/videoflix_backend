import subprocess
import os
from PIL import Image
from django.conf import settings
from django.core.files import File
from .models import Video


def run_command(cmd):
    """
    Executes a shell command and prints its output.
    This function executes the specified command in the system shell. If the command executes successfully, it prints the standard output and standard error (if any) to the console.
    If the command execution fails, it catches the exception and prints the error message from standard error.
    Parameters:
    cmd (str): The shell command to execute.
    Returns:
    None
    Raises:
    subprocess.CalledProcessError: If the command execution fails, this exception is caught and handled by printing the error message from standard error.
    Examples:
    >>> run_command('echo "Hello, World!"')
    Hello, World!
    >>> run_command('cat nonexistentfile.txt')
    Error: cat: nonexistentfile.txt: No such file or directory
    """
    try:
        result = subprocess.run(cmd, capture_output=True, shell=True, check=True)
        print(result.stdout.decode())
        print(result.stderr.decode())
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr.decode()}")

def generate_thumbnail(video_file, thumbnail_file, compression_level=6):
    """
    Generates a compressed PNG thumbnail image for a given video file.
    
    This function uses the `ffmpeg` command-line tool to extract a frame from the specified video file,
    saves it as a thumbnail image file, and then compresses the image using Pillow.
    
    Args:
        video_file (str): The path to the video file for which the thumbnail needs to be generated.
        thumbnail_file (str): The path where the thumbnail image will be saved.
        compression_level (int): The compression level for the saved PNG thumbnail (default is 6, range is 0-9).
    
    Returns:
        str or None: The path to the created thumbnail image file if the creation was successful, `None` otherwise.
    
    Raises:
        OSError: If the `ffmpeg` command fails or if the thumbnail file is not created.
    
    Example:
        >>> thumbnail_path = generate_thumbnail('example_video.mp4', 'example_thumbnail.png')
        >>> print(thumbnail_path)
        'example_thumbnail.png'
    """
    cmd = f'ffmpeg -i "{video_file}" -ss 00:00:01.000 -vframes 1 "{thumbnail_file}"'
    run_command(cmd)
    if os.path.exists(thumbnail_file):
        with Image.open(thumbnail_file) as img:
            img.save(thumbnail_file, 'PNG', compress_level=compression_level, optimize=True)
        return thumbnail_file
    else:
        return None

def save_thumbnail_to_model(video_id, thumbnail_file):
    """
    Saves a thumbnail image file to the associated video model.
    This function retrieves a video instance from the database using the provided video_id.
    It then opens the specified thumbnail file in binary read mode and saves the file to the
    thumbnails field of the video instance. It uses the basename of the thumbnail file as the
    name under which the file is saved in the database. The function prints a confirmation
    message indicating that the thumbnail has been successfully saved.
    :param video_id: The ID of the video to which the thumbnail will be attached.
    :type video_id: int
    :param thumbnail_file: The path to the thumbnail image file.
    :type thumbnail_file: str
    """
    video = Video.objects.get(id=video_id)
    with open(thumbnail_file, 'rb') as f:
        video.thumbnails.save(os.path.basename(thumbnail_file), File(f), save=True)
    


def convert_360p(source, video_id):
    """
    Converts a given video file to 360p resolution using ffmpeg.
    This function takes a source video file and a video ID, converts the video to 360p resolution,
    and then optionally transcodes it into HLS format if the conversion is successful.
    Parameters:
    source (str): The file path of the source video to be converted.
    video_id (str): A unique identifier for the video, used in subsequent processing.
    The conversion process involves the following steps:
    1. Generating a new filename for the 360p video by appending '_360p.mp4' to the original filename.
    2. Constructing and running an ffmpeg command to convert the video resolution to 640x360, encode video using libx264,
       set the CRF (constant rate factor) to 23, and encode audio using AAC.
    3. Checking if the converted file exists. If it does, the function calls `convert_hls` to transcode it to HLS format.
       If the file does not exist, it logs an error message indicating the failure of file creation.
    Notes:
    The function assumes ffmpeg is installed and available in the system path.
    Errors in the ffmpeg conversion process are handled by checking the existence of the output file but are not explicitly
    caught in the command execution.
    Raises:
    FileNotFoundError: If the ffmpeg command fails to create the output file, indicated by the absence of the expected output file.
    """
    print(f"Converting {source} to 360p")
    target = source.replace('.mp4', '_360p.mp4')
    cmd = f'ffmpeg -i "{source}" -s 640x360 -c:v libx264 -crf 23 -c:a aac -strict -2 "{target}"'
    run_command(cmd)
    if os.path.exists(target):
        convert_hls(target, '360p', video_id)
    else:
        print(f"Fehler: 360p Datei {target} wurde nicht erstellt.")

def convert_720p(source, video_id):
    """
    Converts a given video file to 720p resolution using ffmpeg.
    This function takes a source video file and a video ID, converts the video to 720p resolution,
    and then optionally transcodes it into HLS format if the conversion is successful.
    Parameters:
    source (str): The file path of the source video to be converted.
    video_id (str): A unique identifier for the video, used in subsequent processing.
    The conversion process involves the following steps:
    1. Generating a new filename for the 720p video by appending '_720p.mp4' to the original filename.
    2. Constructing and running an ffmpeg command to convert the video resolution to 640x360, encode video using libx264,
       set the CRF (constant rate factor) to 23, and encode audio using AAC.
    3. Checking if the converted file exists. If it does, the function calls `convert_hls` to transcode it to HLS format.
       If the file does not exist, it logs an error message indicating the failure of file creation.
    Notes:
    The function assumes ffmpeg is installed and available in the system path.
    Errors in the ffmpeg conversion process are handled by checking the existence of the output file but are not explicitly
    caught in the command execution.
    Raises:
    FileNotFoundError: If the ffmpeg command fails to create the output file, indicated by the absence of the expected output file.
    """
    print(f"Converting {source} to 720p")
    target = source.replace('.mp4', '_720p.mp4')
    cmd = f'ffmpeg -i "{source}" -s hd720 -c:v libx264 -crf 23 -c:a aac -strict -2 "{target}"'
    run_command(cmd)
    if os.path.exists(target):
        convert_hls(target, '720p', video_id)
    else:
        print(f"Fehler: 720p Datei {target} wurde nicht erstellt.")

def convert_1080p(source, video_id):
    """
    Converts a given video file to 1080p resolution using ffmpeg.
    This function takes a source video file and a video ID, converts the video to 1080p resolution,
    and then optionally transcodes it into HLS format if the conversion is successful.
    Parameters:
    source (str): The file path of the source video to be converted.
    video_id (str): A unique identifier for the video, used in subsequent processing.
    The conversion process involves the following steps:
    1. Generating a new filename for the 1080p video by appending '_1080p.mp4' to the original filename.
    2. Constructing and running an ffmpeg command to convert the video resolution to 640x360, encode video using libx264,
       set the CRF (constant rate factor) to 23, and encode audio using AAC.
    3. Checking if the converted file exists. If it does, the function calls `convert_hls` to transcode it to HLS format.
       If the file does not exist, it logs an error message indicating the failure of file creation.
    Notes:
    The function assumes ffmpeg is installed and available in the system path.
    Errors in the ffmpeg conversion process are handled by checking the existence of the output file but are not explicitly
    caught in the command execution.
    Raises:
    FileNotFoundError: If the ffmpeg command fails to create the output file, indicated by the absence of the expected output file.
    """
    print(f"Converting {source} to 1080p")
    target = source.replace('.mp4', '_1080p.mp4')
    cmd = f'ffmpeg -i "{source}" -s hd1080 -c:v libx264 -crf 23 -c:a aac -strict -2 "{target}"'
    run_command(cmd)
    if os.path.exists(target):
        convert_hls(target, '1080p', video_id)
    else:
        print(f"Fehler: 1080p Datei {target} wurde nicht erstellt.")

def convert_hls(target, resolution, video_id):
    """
    Converts a video file to HLS (HTTP Live Streaming) format.
    This function takes a video file, uses the ffmpeg tool to convert it to the HLS format,
    and saves the resulting .m3u8 playlist to the model. If the conversion is successful, the
    new HLS file's details are saved with the specified video ID and resolution.
    Parameters:
        target (str): The path of the original video file that needs to be converted.
        resolution (str): The resolution of the video, which is stored for reference.
        video_id (int): The database ID for the video, used to associate the converted file.
    Returns:
        None. Outputs information to the console regarding the success or failure of the
        conversion process.
    Raises:
        OSError: If the HLS file is not created, an error message is printed to the console.
    """
    print(f"Converting {target} to HLS")
    hls_target = target.replace('.mp4', '.m3u8')
    cmd_hls = f'ffmpeg -i "{target}" -codec: copy -start_number 0 -hls_time 10 -hls_list_size 0 -f hls "{hls_target}"'
    run_command(cmd_hls)
    if os.path.exists(hls_target):
        save_to_model(video_id, hls_target, resolution)
    else:
        print(f"Fehler: HLS-Datei {hls_target} wurde nicht erstellt.")

def save_to_model(video_id, hls_target, resolution):
    """
    Saves the HLS file path relative to the MEDIA_ROOT setting into the corresponding resolution field in the Video model.
    Args:
        video_id (int): The ID of the video object to update.
        hls_target (str): The absolute file path of the HLS file to be saved.
        resolution (str): The resolution of the video file ('360p', '720p', '1080p').
    The function first retrieves the video from the database using its `video_id`. It then computes the relative path
    of the `hls_target` using the MEDIA_ROOT setting. Based on the `resolution` provided, it updates the respective
    field of the video object (`video_360p_m3u8`, `video_720p_m3u8`, `video_1080p_m3u8`).
    If all three resolution fields are set, it creates a master playlist for the video. Finally, the updated video
    object is saved back to the database.
    """
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

def create_master_playlist(video):
    """
    Generates a master playlist for a given video object with multiple streaming qualities.
    This function takes a video object that has paths to its various quality versions and 
    creates a master playlist file ('.m3u8') for use in streaming applications. The function
    replaces the '.mp4' extension in the source video file path with '_master.m3u8' to
    denote the master playlist. It writes the playlist directives and the relative paths to
    different quality streams (360p, 720p, 1080p) if they exist.
    Parameters:
    - video (object): An object containing attributes of the video and its different quality versions.
      Expected attributes include:
      - video_file.path (str): Path to the source video file.
      - video_360p_m3u8 (str, optional): Path to the 360p version playlist.
      - video_720p_m3u8 (str, optional): Path to the 720p version playlist.
      - video_1080p_m3u8 (str, optional): Path to the 1080p version playlist.
      - video_master_m3u8 (str, optional): Path to the master playlist to be updated after creation.
    Outputs:
    - A master playlist file is created at the same location as the source video with a name ending in '_master.m3u8'.
    - If successful, updates the video object's 'video_master_m3u8' attribute with the relative path of the master playlist.
    Raises:
    - Prints an error message if the master playlist file cannot be created.
    """
    source = video.video_file.path
    master_playlist_path = source.replace('.mp4', '_master.m3u8')

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
    else:
        print(f"Fehler: Master-Playlist {master_playlist_path} wurde nicht erstellt.")
