from IPython.display import Image

def showpic(ID, w=6, picpath=''):
    """
    display a picture (jpg) in jupyter notebook
    set picture path `picpath`, picture name should ends with numbers
    w ~ width, picpath ~ the folder path contains images
    
    """
    return Image(picpath+'/{}.jpg'.format(ID), width=w*100)