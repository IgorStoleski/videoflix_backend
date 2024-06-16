import subprocess
import os

def run_command(cmd):
    try:
        result = subprocess.run(cmd, capture_output=True, shell=True, check=True)
        print(result.stdout.decode())
        print(result.stderr.decode())
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr.decode()}")

def convert_480p(source):
    target = source.replace('.mp4', '_480p.mp4')
    cmd = f'ffmpeg -i "{source}" -s hd480 -c:v libx264 -crf 23 -c:a aac -strict -2 "{target}"'
    run_command(cmd)
    if os.path.exists(target):
        convert_hls(target, '480p')
    else:
        print(f"Konvertierung fehlgeschlagen: {target} wurde nicht erstellt.")

def convert_720p(source):    
    target = source.replace('.mp4', '_720p.mp4')
    cmd = f'ffmpeg -i "{source}" -s hd720 -c:v libx264 -crf 23 -c:a aac -strict -2 "{target}"'
    run_command(cmd)
    if os.path.exists(target):
        convert_hls(target, '720p')
    else:
        print(f"Konvertierung fehlgeschlagen: {target} wurde nicht erstellt.")

def convert_1080p(source):
    target = source.replace('.mp4', '_1080p.mp4')
    cmd = f'ffmpeg -i "{source}" -s hd1080 -c:v libx264 -crf 23 -c:a aac -strict -2 "{target}"'
    run_command(cmd)
    if os.path.exists(target):
        convert_hls(target, '1080p')
    else:
        print(f"Konvertierung fehlgeschlagen: {target} wurde nicht erstellt.")

def convert_hls(target, resolution):
    hls_target = target.replace('.mp4', '.m3u8')
    cmd_hls = f'ffmpeg -i "{target}" -codec: copy -start_number 0 -hls_time 10 -hls_list_size 0 -f hls "{hls_target}"'
    run_command(cmd_hls)