'''
Simple save and load with json.

Save your time on save & load json file.
'''
import json

def save(obj, path):
    '''Save file'''
    with open(path, 'w') as file:
        json.dump(obj, file)

def load(path):
    '''Load file'''
    with open(path) as file:
        obj = json.load(file)
    return obj

def media(obj, path):
    '''Save & Load file'''
    if obj:
        save(obj, path)
        return obj
    return load(path)
