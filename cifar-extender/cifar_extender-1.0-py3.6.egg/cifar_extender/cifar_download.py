#!/usr/bin/env python3.6

import os
import sys
import csv
import asyncio
from collections import defaultdict

import requests


IMG_DIR = "./images/"


def download_images(loop, image_dir, urls, category, n=100):
    """
    download image from url to disk

    :param loop: event loop for the downloading.
    :type loop: asyncio.AbstractEventLoop()
    :param image_dir: key for the image file, used as the file name
    :type image_dir: str
    :param urls: urls for the image files
    :type urls: list
    :param category: categeory for the image, used to save to a class directory
    :type category: str
    :param n: number of pictures to download
    :type n: int
    :return: None
    :rtype: None
    """
    dir_path = os.path.join(image_dir, category)
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)

    for url in urls:
        if len(os.listdir(dir_path)) >= n:
            break

        file_name = url.split('/')[-1]
        file_path = os.path.join(dir_path, file_name)
        try:
            image = requests.get(url, allow_redirects=False, timeout=2)
        except Exception as e:
            print(e)
            continue

        print("{}/{} - {}: {}".format(len(os.listdir(dir_path)) + 1,
                                      n,
                                      category,
                                      file_name))
        headers = image.headers
        if image.status_code != 200:
            print("\tCONNECTION ERROR {}: {}".format(image.status_code, url))
            # continue
        elif headers['Content-Type'] != 'image/jpeg':
            print("\tFILE TYPE ERROR {}: {}".format(headers['Content-Type'], url))
            # continue
        elif int(headers['Content-Length']) < 50000:  # only files > 50kb
            print("\tFILE SIZE ERROR {}: {}".format(headers['Content-Length'], url))
            # continue
        else:
            with open(file_path, 'wb') as file:
                file.write(image.content)  # download image

    loop.stop()  # escape loop iteration


def get_collection(filename):
    collection = defaultdict(list)
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            category, url = row
            collection[category].append(url)

    return collection


def main(datafile, n=100, img_dir=None):
    if len(sys.argv) > 1:
        n = int(sys.argv[1])

    if not img_dir:
        img_dir = IMG_DIR
    if not os.path.exists(img_dir):
        os.mkdir(img_dir)

    d = get_collection(datafile)
    loop = asyncio.get_event_loop()  # async event loop
    for k in d.keys():
        loop.call_soon(download_images, loop, img_dir, d[k], k, n)

    loop.run_forever()  # execute queued work
    loop.close()  # shutdown loop


if __name__ == "__main__":
    main('data/images.csv', n=100)
