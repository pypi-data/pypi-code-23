from IPython.display import Image

picpath=''
def showpic(ID, w=6, picpath=picpath):
    """
    display a picture (jpg) in jupyter notebook
    set picture path `picpath`, picture name should ends with numbers
    
    """
    return Image(picpath+'/{}.jpg'.format(ID), width=w*100)