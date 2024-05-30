import subprocess

def convert_480p(source):
    print('start to convert')
    target = source.replace('.mp4', '_480p.mp4')
    print(target)
    cmd = f'ffmpeg -i "{source}" -s hd480 -c:v libx264 -crf 23 -c:a aac -strict -2 "{target}"'
    subprocess.run(cmd, shell=True, check=True)
    
    
    
def convert_720p(source):    
    target = source.replace('.mp4', '_720p.mp4')
    cmd = f'ffmpeg -i "{source}" -s hd720 -c:v libx264 -crf 23 -c:a aac -strict -2 "{target}"'    
    subprocess.run(cmd, capture_output=True, shell=True)
    
    
