"""
MIT License
Copyright (c) 2017 Roni Eliezer
"""

class Docker(object):
    '''
    Args:
        image_name (str):     docker image name
        container_name (str): docker container name
    '''


    def __init__(self, image_name, container_name):
        '''
        Constructor
        '''
        self.image_name     = image_name
        self.container_name = container_name
        