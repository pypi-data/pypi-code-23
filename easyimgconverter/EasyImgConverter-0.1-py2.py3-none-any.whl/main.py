
# Imports

import EasyImgConverter
import os, imageio
import argparse

# Definition of the functions


def main():

    print 'EasyImgConverter v.{}'.format(EasyImgConverter.__version__)

    ap = argparse.ArgumentParser()

    ap.add_argument("-t", "--type", required=True, choices=['png','jpg','tif'], help="Type of image format. ")
    ap.add_argument("-i", "--imgpath", required=True,nargs='+', help="Path of the image to convert. ")

    args = vars(ap.parse_args())
    target_format = str(args["type"])
    path_img_list = args["imgpath"]

    for current_img in path_img_list:

        if not os.path.isdir(current_img):

            
            convert_img(current_img,target_format)

        else:

            print "Input path is a directory. Please try again."
            break;

    print "Conversion done."

# Calling the script

if __name__ == '__main__':
    main()


def convert_img(path_img,target_format):

    img = imageio.imread(path_img)
    tmp_path, file_name = os.path.split(path_img)
    only_name, only_extension = os.path.splitext(file_name)

    if (target_format == 'png'):
        imageio.imwrite(os.path.join(tmp_path,only_name + '.png'),img)

    if (target_format == 'tif'):
        imageio.imwrite(os.path.join(tmp_path,only_name + '.tif'),img)

    if (target_format == 'jpg'):
        imageio.imwrite(os.path.join(tmp_path,only_name + '.jpg'),img)










