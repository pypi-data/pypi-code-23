import os


def store(route_images,route_text,route_audio,route_video):
   
    """Verify the existence of directories.
    
    Using the routes provided by the file, check the routes and create 
    the audio storage directory.

    Args:
        route_images (srt): Image directory path.
        route_text (str): Text directory path.
        route_audio (str): Audio directory path.
        route_video (str): Video directory path.
        
    Returns:
        Output in console warning non-existence.
        
    """
    if not os.path.exists(route_images) or not os.path.exists(route_text) or not os.path.exists(route_video):
        print('Some of the routes do not exist')
    
    else: 
        if not os.path.exists(route_audio): os.makedirs(route_audio)
        
            
    
def existence(file):
    """Extracts information from file paths.
    
    Args:
    file (file): File with specific format to generate the video.
    
    Returns:
    img (str): Name of each image included in the video in order.
    text (str): Name of each text file included corresponding to each image.
    language (str): Voice for festival.
    routes (str): Name of routes.
    
    """
    f = open(file,'r')
    file = f.readlines()
    
    language = file[0].split(' \n')[0]
    
    img = [] 
    text = []
    
    file_1 = file[1:file.index('\n')] 
    file_2 = file[file.index('\n')+1:]
    
    # Get image name and text name   
    img = [i.split('>')[0] for i in file_1]  
    text = [i.split('>')[1].split('\n')[0] for i in file_1]
    
    # Get routes specified in the file
    routes = [i.split('=')[1].split('\n')[0] for i in file_2]  
    
    return img,text,language,routes
        
        
        
        



