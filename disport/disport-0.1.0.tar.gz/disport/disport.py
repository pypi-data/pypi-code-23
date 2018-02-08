#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from .command import Command
from .display import Display
from .display import Resolution


class Controller:
    """Reads output of 'xrandr -q' to get all connected displays
    and their resolutions.
    Stores available displays.
    Handles user input to determine the respective xrandr commands.

    Provides the following methods:
        1) get_common_resolutions()
        2) print_status()
        3) get_built_in_display()
        4) reduce_output(display)
        5) clone_output()
        6) extend_output(diretion)
    """
    def __init__(self):
        """Get connected displays and their resolutions."""
        cmd = Command("xrandr -q")
        output = cmd.call(feedback=True).strip().split("\n")
        self._displays = []
        # Iterate over xrandr output
        for i, dispLine in enumerate(output):
            # Detect connected displays
            if " connected" in dispLine:
                displayName = dispLine.split(" ")[0]
                resolutions = []
                # Get available resolutions
                for resLine in output[i+1:]:
                    if resLine.startswith(" "):
                        resLine = resLine.strip(" ").split(" ")[0]
                        res = Resolution(resLine)
                        resolutions.append(res)
                    else:
                        break
                # Store display data
                disp = Display(displayName, resolutions)
                self._displays.append(disp)
        # Assume that the first display listed by xrandr is the main one.
        self._builtIn = self._displays[0]

    def get_common_resolutions(self):
        """Return list of resolutions shared by all connected displays."""
        # Create copy of first display
        dummy = Display("Dummy", self._builtIn.get_resolutions())
        # Iterate over remaining displays
        for disp in self._displays[1:]:
            # Create dummy display with intersection of all resolutions
            dummy = Display("Dummy", dummy & disp)
        return dummy.get_resolutions()

    def print_status(self, message):
        """Print final message about what the program just did
        before exiting.
        """
        print(message)
        sys.exit(0)

    def get_built_in_display(self):
        """Return built-in display."""
        return self._builtIn

    def reduce_output(self, disp):
        """Reduce the output to single display.
        The resolution is determined automatically by xrandr.
        """
        # Set output to display disp
        cmd = Command("xrandr")
        cmd += "--output"
        cmd += str(disp)
        cmd += "--auto"
        cmd += "--rotate normal"
        cmd += "--pos 0x0"
        # Turn off output of all other displays
        for disp in (x for x in self._displays if x != disp):
            cmd += "--output " + str(disp) + " --off"
        cmd.call()
        self.print_status("Reduced output.")

    def clone_output(self):
        """Clone output to all registered displays.
        Use the highest shared resolution.
        """
        if len(self._displays) < 2:
            print("Cannot clone: Not enough displays connected.")
            sys.exit(1)
        else:
            # Make sure each display gets the same resolution
            res = str(max(self.get_common_resolutions()))
            cmd = Command("xrandr")
            for disp in self._displays:
                cmd += "--output " + str(disp)
                cmd += "--mode " + res
                cmd += "--rotate normal"
                cmd += "--pos 0x0"
            cmd.call()
            self.print_status("Cloned output.")

    def extend_output(self, direction):
        """Extend the output to displays left or right
        of the built-in display.
        The resolution is determined automatically by xrandr.
        """
        if len(self._displays) < 2:
            print("Cannot extend output: Not enough displays connected.")
            sys.exit(1)
        else:
            # Normalize direction
            if direction in ("right", "r"):
                direction = "right"
            elif direction in ("left", "l"):
                direction = "left"
            else:
                print("Unknown direction:", direction)
                print("Choose either l (left) or r (right).")
                sys.exit(1)
            # Set output for built-in display
            cmd = Command("xrandr")
            cmd += "--output " + str(self._builtIn)
            cmd += "--auto"
            cmd += "--rotate normal"
            cmd += "--pos 0x0"
            # Set output for remaining display
            prev = self._builtIn
            for disp in (x for x in self._displays if x != self._builtIn):
                cmd += "--output " + str(disp)
                cmd += "--auto"
                cmd += "--rotate normal"
                cmd += "--" + direction + "-of " + str(prev)
                prev = disp
            cmd.call()
            self.print_status("Extended output.")

    def list_displays(self):
        """List connected displays and their available resolutions."""
        for display in self._displays:
            print(display)
            for resolution in display.get_resolutions():
                print("  " + str(resolution))

    def print_help(self):
        """List available options."""
        print("  -c, --clone\tClone output to external display")
        print("  -e, --extend")
        print("\tleft\tExtend output to the left")
        print("\tright\tExtend output to the right")
        print("  -s, --solo\tReduce output to primary display")
        print("  -l, --list\tList available displays")

def main():
    """Parse arguments and call the respective methods."""
    c = Controller()
    # Quit program if too few arguments are provided.
    if len(sys.argv) < 2:
        c.print_help()
        sys.exit(1)
    else:
        args = sys.argv[1:]
        mode = args[0]
        # Clone output
        if mode in ("--clone", "-c"):
            c.clone_output()
        # Extend output
        elif mode in ("--extend", "-e"):
            c.extend_output(args[1])
        # Reduce output to single display
        elif mode in ("--solo", "--single", "-s"):
            c.reduce_output(c.get_built_in_display())
        # List displays
        elif mode in ("--list", "-l"):
            c.list_displays()
        elif mode in ("--help", "-h"):
            c.print_help()
        # Unknown command, so quit program
        else:
            print("Unknown option:", mode)
            print("Use option -h (--help) to list available options.")
            sys.exit(1)
