#!/usr/bin/env python2

import gtk.gdk
import cv2

import tempfile
import shutil
import os
import time
from subprocess import Popen, PIPE
import sys
import json

class PautoProgram():
    def __init__(self, script_file):
        self.dirpath = tempfile.mkdtemp()
        self.step_number = 0
        self.script_file = script_file
        with open(script_file) as f:
            self.script = json.load(f)
        self.steps = self.script["steps"]
        self.template_dir = os.path.join(os.path.dirname(self.script_file), self.script["templateDir"])

    def xdotool(self, command):
        return Popen("xdotool %s" % command, stdout=PIPE, shell=True).stdout.read()

    def getmouselocation(self):
        x, y, screen, window = map(
                lambda tmp: int(tmp.split(":")[1]),
                self.xdotool("getmouselocation").split(" "))

        return (x, y)

    def mousemove(self, x, y):
        cur_x, cur_y = self.getmouselocation()
        new_x = cur_x
        new_y = cur_y

        if new_x == x and new_y == y:
            return

        while (new_x != x) or (new_y != y):
            if new_x > x:
                new_x -= 1
            elif new_x < x:
                new_x += 1

            if new_y > y:
                new_y -= 1
            elif new_y < y:
                new_y += 1

            self.xdotool("mousemove %i %i" % (new_x, new_y))

        time.sleep(1)

    def cleanup(self):
        shutil.rmtree(self.dirpath)

    def screenshot(self, step_number):
        filename = "%s/step-%0.3i.png" % (self.dirpath, step_number)

        root_window = gtk.gdk.get_default_root_window()
        root_size = root_window.get_size()

        pb = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, root_size[0], root_size[1])
        pb = pb.get_from_drawable(root_window, root_window.get_colormap(), 0, 0, 0, 0, root_size[0], root_size[1])
        pb.save(filename, "png")

        return filename

    def has_more_steps(self):
        return os.path.isfile("%s/%0.3i.png" % (self.template_dir, self.step_number))

    def step(self):
        filename = self.screenshot(self.step_number)
        template_filename = "%s/%0.3i.png" % (self.template_dir, self.step_number)

        method = cv2.TM_SQDIFF_NORMED

        # Read the images from the file
        template = cv2.imread(template_filename, 0)
        image = cv2.imread(filename, 0)

        width, height = template.shape[::-1]

        result = cv2.matchTemplate(image, template, method)

        # TODO: Figure out what this copypasta'd code does.
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        # Get the outer positions of the match.
        left, top = min_loc
        right, bottom = (left + width), (top + height)

        # Move the mouse to the specified location.
        self.mousemove(left + (width / 2), top + (height / 2))

        self.xdotool(self.steps[self.step_number])
        time.sleep(2)

        self.step_number += 1

        return self.step_number

    def run(self):
        while self.has_more_steps():
            self.step()
        self.cleanup()
        pass

if __name__ == '__main__':
    if len(sys.argv) == 1 or "--help" in sys.argv or "-h" in sys.argv:
        print("Usage: %s JSON_SCRIPT" % sys.argv[0])
        exit(1)

    program = PautoProgram(sys.argv[1])
    program.run()
