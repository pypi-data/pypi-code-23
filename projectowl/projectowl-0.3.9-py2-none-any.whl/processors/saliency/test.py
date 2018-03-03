"""Test saliency methods.
"""

import rbd
import mbd
import ft
import binarise as bina
from PIL import Image
import time
import skimage.io

# path to the image
filename = 'bird.jpg'
img_arr = skimage.io.imread(filename)

startt = time.time()
# get the saliency maps using the 3 implemented methods
rbd_res = rbd.get_saliency_rbd(img_arr).astype('uint8')
print "rbd time: {}s".format(time.time() - startt)

startt = time.time()
ft_res = ft.get_saliency_ft(img_arr).astype('uint8')
print "ft time: {}s".format(time.time() - startt)

startt = time.time()
mbd_res = mbd.get_saliency_mbd(img_arr).astype('uint8')
print "mbd time: {}s".format(time.time() - startt)

# often, it is desirable to have a binary saliency map
binary_sal = bina.binarise_saliency_map(mbd_res, method='adaptive')

img = Image.open(filename)
# img = cv2.imread(filename)

img.show(title="input")
rbd_res = Image.fromarray(rbd_res)
ft_res = Image.fromarray(ft_res)
mbd_res = Image.fromarray(mbd_res)
rbd_res.show("rbd")
ft_res.show("ft")
mbd_res.show("mbd")

#openCV cannot display numpy type 0, so convert to uint8 and scale
binary = Image.fromarray(255 * binary_sal.astype('uint8'))
binary.show("binary")
