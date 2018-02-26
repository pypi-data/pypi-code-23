# __init__.py

import os

file_name = "phrases.txt"

current_path = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_path, file_name)

file_handler = open(file_path)

phrases = [phrase.strip() for phrase in file_handler.readlines()]

from .cookie import fortune
