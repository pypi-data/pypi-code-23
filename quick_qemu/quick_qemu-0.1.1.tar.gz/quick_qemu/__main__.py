#! /usr/bin/env python3

import sys

from quick_qemu import main as quick_qemu_main

def main():
    quick_qemu_main(sys.argv[1:])

if __name__ == "__main__":
    main()
