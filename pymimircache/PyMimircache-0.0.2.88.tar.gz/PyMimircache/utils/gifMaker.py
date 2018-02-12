# coding=utf-8
import glob
import os

import imageio
from PIL import Image

DIRECTORY = '/tmp/PyMimircache'


def get_image_order_original(filename):
    return int(filename.split("/")[-1].split("_")[-1][:-4])

def get_image_order1205(filename):
    return float(filename.split("/")[-1].split("_")[1][:-4])

def sort_filenames(filenames, get_image_order):
    # return sorted(filenames, key=lambda x: int(x.split('/')[-1].split('_')[-1][:-4]))
    return sorted(filenames, key=get_image_order)


def create_animation(folder_loc, filename_pattern="*.png", duration=0.6,
                     get_image_order=get_image_order_original, **kwargs):
    """
    create animation from images in the folder
    :param folder_loc:
    :param filename_pattern:
    :param duration:
    :param get_image_order:
    :param kwargs:
    :return:
    """
    if not os.path.exists(DIRECTORY):
        os.makedirs(DIRECTORY)
    gifname = kwargs.get("gifname", "animation.gif")
    gif_list = []
    images = []
    for fileloc in glob.glob("{}/{}".format(folder_loc, filename_pattern)):
        print(fileloc)
        if not get_image_order(fileloc) in gif_list:
            gif_list.append(get_image_order(fileloc))
            im = Image.open(fileloc)
            im.save("{}/gifMaker_{}.png".format(DIRECTORY, get_image_order(fileloc)))

    gif_list.sort()
    print(gif_list)
    for file_order in gif_list:
        images.append(imageio.imread("{}/gifMaker_{}.gif".format(DIRECTORY, file_order)))
    imageio.mimsave("{}/{}".format(folder_loc, gifname), images, duration=duration)
    print("saved to {}/{}".format(folder_loc, gifname))



if __name__ == "__main__":
    offline_plotting('/home/jason/pycharm/mimircache/A1a1a11a/',
                     filename_pattern="akamai_0.*.png", get_image_order=get_image_order1205)
