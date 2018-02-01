from os.path import join
from scipy.misc import imresize, imread

import numpy as np
import chainer
from chainer.datasets import LabeledImageDataset
from chainer_addons.utils.imgproc import Augmentation


class ImageDataset(LabeledImageDataset):
	label_shift = 1
	def __init__(self, opts,
			preprocess=None, augment=None, return_orig=False, mean=None,
			*args, **kw):
		super(ImageDataset, self).__init__(*args, **kw)
		self.augment = augment if augment is not None else opts.augment

		self.mean = mean

		self._size = (opts.size, opts.size)
		self._interp = "bilinear"
		self._preprocess = preprocess

		self.augmentor = Augmentation()
		self.augmentor.random_crop(self._size).random_horizontal_flip()

		self.return_orig = return_orig

	def preprocess(self, orig):
		def inner(img, size):
			if self._preprocess is not None and callable(self._preprocess):
				return self._preprocess(img, size=size)
			return imresize(img, size, interp=self._interp).astype(self._dtype).transpose(2, 0, 1)

		if self.augment and chainer.config.train:
			augment_size = tuple(int(s / .875) for s in self._size)
			return self.augmentor(inner(orig, augment_size))
		else:
			return inner(orig, self._size)


	def get_example(self, i):
		im_name, int_label = self._pairs[i]
		orig = imread(join(self._root, im_name), mode="RGB")
		label = np.array(int_label + ImageDataset.label_shift, dtype=self._label_dtype)
		if self.return_orig:
			return orig, self.preprocess(orig), label
		else:
			return self.preprocess(orig), label


def create(opts, data, images_folder="images", *args, **kw):
	return ImageDataset(opts,
		pairs=join(opts.root, data),
		root=join(opts.root, images_folder),
		*args, **kw)
