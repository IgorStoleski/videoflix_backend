import subprocess

def convert_480p(source):
    target = source[:4] + '_480p.mp4'
    cmd = 'ffmpeg -i "{}" -s hd480 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"'.format(source, target)
    subprocess.run(cmd, capture_output=True, shell=True)
    
    
""" def convert_720p(source):    
    new_file_name = source + _720p.mp4
    cmd = 'ffmpeg -i "{}" -s hd720 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"'.format(source, new_file)    
    run = subprocess.run(cmd, capture_output=True, shell=True) """
    
    
