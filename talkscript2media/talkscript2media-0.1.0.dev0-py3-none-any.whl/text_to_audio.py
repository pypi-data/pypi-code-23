import shlex
import subprocess
import re
import os


def number_images(route_images):
    """Extract the number of images from a directory.
    
    Args:
    route_images (str): Route of images
    
    Returns:
    N (int): Number of images
    
    """
    path, dirs, files = os.walk(route_images).__next__()
    N = len(files)
    return N


def audio_festival(route_text, route_audio, text, language, N):
    """It generates audios from ffmpeg and texts.
    
    Args:
    route_text (str): Route of text files. 
    route_audio (str): Route of audio. 
    text (str): Name of each text.
    language (str): Voice for festival.
    N (int): Number of images necessarily equal to the number of text files.
    
    Returns:
    N audio files
    
    """
    log = open('process.log', 'a') # File log 
    log.write('Audio_festival')
    log.flush()
    
    print('Text to Audio....')
    print(language)

    for i in range(N):
        command_line ='text2wave '+route_text + '/' + text[i] + ' -o ' \
            + route_audio + '/0%d.wav '%i+' '+' -eval ''('+language+')'''   
        args = shlex.split(command_line)
        c = subprocess.Popen(args, stdout=log, stderr=log)

        
def duration(N, route_images, route_audio, img):
    """Get the duration of each audio file.
    
    Args:
    N (int): Number of images .
    route_images (str): Route of images.
    route_audio (str): Route of audio.
    img (str): Name of the images.
    
    Returns:
    Duration.txt (file): Generates a file with the duration of each audio,
    with the format specified by ffmpeg.
    
    """
    f= open('Duration.txt','w')
    f.write('ffconcat version 1.0\n')
    
    for i in range(N):
        
        f.write('file '+route_images+'/'+img[i]+' \n')
        process = subprocess.Popen(['ffmpeg', '-i', route_audio+'/0%d.wav'%i], \
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out, _ = process.communicate()
        result = re.search(r"Duration:\s{1}(?P<hours>\d+?):(?P<minutes>\d+?):(?P<seconds>\d+\.\d+?),",\
        out.decode('utf-8'), re.DOTALL).groupdict()
        f.write('duration  '+result['seconds']+'\n')
        
    f.close()
