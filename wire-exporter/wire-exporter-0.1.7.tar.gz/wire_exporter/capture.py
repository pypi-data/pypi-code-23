import atexit
import os
from subprocess import Popen, DEVNULL


def start_capture(interface, interval, output_path):
    prepare_directory(output_path)
    captures = get_captures(output_path, exclude_newest=False)
    for capture in captures:
        os.remove(capture)
    o = Popen(("dumpcap", "-b", "duration:{}".format(interval), "-i", interface, "-w", output_path), stdout=DEVNULL,
              stderr=DEVNULL)
    atexit.register(o.terminate)
    return o


def get_captures(path, exclude_newest=True):
    files = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    if len(files) is 0:
        return []
    youngest_file = None
    youngest_lm = 0
    for file in files:
        lm = os.path.getmtime(file)
        if lm > youngest_lm:
            youngest_file = file
            youngest_lm = lm

    if exclude_newest:
        files.remove(youngest_file)
    return files


def prepare_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)
