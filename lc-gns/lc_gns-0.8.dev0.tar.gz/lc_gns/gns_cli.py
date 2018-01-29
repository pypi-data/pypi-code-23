from __future__ import print_function
from gns_api import GNS_api
import argparse
import sys



def main():
    arguments = list(sys.argv[1:])

    if sys.argv[1] == ("--seq") and \
        sys.argv[3] == ("--space") and \
            sys.argv[5] == ("--width") and \
                len(sys.argv[4]) == 4 and \
                    len(arguments) == 6:
        
        parser = argparse.ArgumentParser()
        parser.add_argument('--seq', type=str)
        parser.add_argument('--space', type=str)
        parser.add_argument('--width', type=str)

        args = parser.parse_args()
        args.seq= ((args.seq).strip('[').strip(']'))
        args.space=((args.space).strip('(').strip(')'))
        space = args.space.split(',')

        sequence = list(map(int, args.seq.split(',')))
        min_spacing = int(space[0])
        max_spacing = int(space[1])
        image_width = int(args.width)

        gns_api_object = GNS_api()
        img = gns_api_object.gns(sequence, (min_spacing, max_spacing), image_width)
        gns_api_object.save_img(img, sequence)
    else:
        print("\nInput error!")
        print("Usage  : python gns_cli.py --seg <digits>  --space <min_space,max_space>   --width <max_width>")
        print("Example: python gns_cli.py --seq   1,2     --space   0,10                  --width   66\n")
        # main()


if __name__ == "__main__":
    main()
