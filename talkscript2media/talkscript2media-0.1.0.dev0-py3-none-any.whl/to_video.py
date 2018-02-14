import shlex
import subprocess
import time


def image_video(r_video):
    """Generating video from images and archive duration
    with format specifited by ffmpeg.
    
    Args:
    r_video (str): Route of video.
    
    Returns:
    Video0.mp4 (video): Video of images each with specific duration.
    
    """
    log = open('process.log', 'a') # File log 
    log.write('image_video\n')
    log.flush()  
    print('Image to video...')
    
    
    command_line = 'ffmpeg -i Duration.txt -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2"  '+r_video+'/Video0.mp4'
    args = shlex.split(command_line)
    c = subprocess.Popen(args, stdout=log, stderr=log)


def u_audios(N,route_audio):
    """Concatenate audios.
    
    Args:
    N (int): Number of images.
    route_audio (str): Route of audio files.
    
    Returns:
    audio.wav (file): Audio union.
    Aud.txt (file): Archivo for  union of audios with ffmpeg.
    
    """
    log = open('process.log', 'a')
    log.write('U_Audios\n')
    log.flush()
    print('Concatenating audios')
    
    f = open('Aud.txt', 'w')
    
    for i in range(N):
        
        f.write('file '+route_audio+'/0%d.wav \n'%i)
    f.close()
    command_line = 'ffmpeg -f concat -safe 0 -i Aud.txt -c copy ' + route_audio \
        + '/audio.wav'
    args = shlex.split(command_line)
    c = subprocess.Popen(args, stdout=log, stderr=log)


def video_u_audio(route_audio, route_video, name_video):
    """Join audio and video.
    
    Args:
    route_audio (str): Route audio.
    route_video (str): Rote video.
    name_video (str): Output video name.
    
    Returns:
    video (file): Video. 
    
    """
    log = open('process.log', 'a')
    log.write('Video_U_Audio\n')
    log.flush() 
    print('Video.............')
    
    command_line = 'ffmpeg -i '+route_video+'/Video0.mp4 -i '+route_audio+'/audio.wav -strict -2 '+route_video+'/'+name_video
    args = shlex.split(command_line)
    c = subprocess.Popen(args,stdout=log, stderr=log).communicate()




