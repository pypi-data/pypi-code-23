import cv2
import numpy as np
import imgaug
from imgaug import augmenters, parameters
from skimage.draw import polygon

__all__ = ['XShift', 'ColorTransfer', 'Polygons', 'ObjectInsertion']


class XShift(augmenters.Augmenter):
    """
    Stealth augmentation, its usage is too specific for proper publication. It shifts an image to the left or right by cropping the left or right edge.
    """
    def __init__(self, shift, name=None, deterministic=False, random_state=None):
        super(XShift, self).__init__(name=name, deterministic=deterministic, random_state=random_state)
        assert type(shift) is int or shift is None, 'Expected int or None, got {}'.format(type(shift))
        self._shift = shift

    def _augment_images(self, images, random_state, parents, hooks):
        """Crops image left or right. """
        if self._shift is None:
            return images

        result = images
        nb_images = len(images)
        for i in range(nb_images):
            tr_x = self._shift
            img_width = images[i].shape[1]
            # On negative transform crop the left side else the right side.
            col_start = int(0 if tr_x >= 0 else abs(tr_x))
            col_end = int(img_width if tr_x < 0 else img_width - tr_x)

            result[i] = images[i][:, col_start:col_end, :]
        return result

    def _augment_keypoints(self, keypoints_on_images, random_state, parents, hooks):
        return keypoints_on_images

    def get_parameters(self):
        return [self._shift]


class Polygons(augmenters.Augmenter):
    """
    Source code at http://cglab.ca/~sander/misc/ConvexGeneration/convex.html
    """

    def __init__(self, polys=(3, 7, 3), vertices=(5, 9, 3), per_channel=False, name=None, deterministic=False,
                 random_state=None):
        """
        
        
        :param polys Expects a 3-length tuple (min, mean, std), defining the minimum and normal distribution of the number of polygons to be drawn over the image
        :param vertices Expects a 3-length tuple (min, mean, std), defining the minimum and normal distribution of the number of vertices per polygon to be drawn over the image
        :param per_channel Expects a bool or value, defining the chance the polygons alter single channels rather than all channels.
        """
        super(Polygons, self).__init__(name=name, deterministic=deterministic, random_state=random_state)
        for pv in [polys, vertices]:
            assert imgaug.is_iterable(pv), 'Expected list or tuple, got {} instead.'.format(polys)
            assert len(pv) == 3, 'Expected iterable to be of length 3, got {} instead.'.format(len(pv))
            assert len([x for x in pv if type(x) is int]) == len(pv), 'Not all values are ints.'

        self._poly, self._vertex = polys, vertices

        if per_channel in [True, False, 0, 1, 0.0, 1.0]:
            self.per_channel = parameters.Deterministic(int(per_channel))
        elif imgaug.is_single_number(per_channel):
            assert 0 <= per_channel <= 1.0
            self.per_channel = parameters.Binomial(per_channel)
        else:
            raise Exception("Expected per_channel to be boolean or number or StochasticParameter")

    def _augment_images(self, images, random_state, parents, hooks):
        result = images
        nb_images = len(images)
        for i in range(nb_images):
            image = images[i]
            mask = np.ones((image.shape[0], image.shape[1]), dtype=np.float16)

            poly_min, poly_mean, poly_std = self._poly
            polygon_count = int(np.maximum(poly_min, np.random.normal(poly_mean, poly_std)))
            for p in range(polygon_count):
                yy, xx = self._create_polygon(image, mask)
                f = np.random.normal(0.5, 0.2)
                mask[yy, xx] *= min(1 - f, 0.8) if f < 0.5 else max(2 - f, 1.2)

            per_channel = self.per_channel.draw_sample()
            image = image.astype("float16") if per_channel else cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype("float16")

            ch = np.random.randint(0, 3) if per_channel else 2
            image[:, :, ch] *= mask
            image[:, :, ch] = np.clip(image[:, :, ch], 0, 255)

            image = image.astype("uint8") if per_channel else cv2.cvtColor(image.astype("uint8"), cv2.COLOR_HSV2BGR)
            result[i] = image

        return result

    def _create_polygon(self, image, mask):
        vertex_min, vertex_mean, vertex_std = self._vertex
        # generate random x,y points, making sure the final polygon is no larger than 25% of the image
        vertex_count = int(max(vertex_min, np.random.normal(vertex_mean, vertex_std)))

        x_pool = np.random.randint(low=0, high=image.shape[1] / 2, size=vertex_count)
        x_pool.sort()
        y_pool = np.random.randint(low=0, high=image.shape[0] / 2, size=vertex_count)
        y_pool.sort()

        # divide into chains of points
        def create_vector(pool):
            vect = []
            l, r = pool[0], pool[0]
            for i in range(1, len(pool)):
                v = pool[i]
                if np.random.rand() < 0.5:
                    vect.append(v - l)
                    l = v
                else:
                    vect.append(r - v)
                    r = v
            vect.append(pool[-1] - l)
            vect.append(r - pool[-1])
            return vect

        xvec = create_vector(x_pool)
        yvec = create_vector(y_pool)

        # pair up xy and combine into vectors
        np.random.shuffle(yvec)
        vec = []
        for i in range(vertex_count):
            vec.append((xvec[i], yvec[i]))

        # sort vectors by angle and lay them end to end
        vec.sort(key=lambda v: np.arctan2(v[1], v[0]))

        x = y = minx = miny = maxx = maxy = 0
        xpoints, ypoints = [], []
        for i in range(vertex_count):
            xpoints.append(x)
            ypoints.append(y)
            x += vec[i][0]
            y += vec[i][1]
            maxx = max((maxx, x))
            maxy = max((maxy, y))
            minx = min((minx, x))
            miny = min((miny, y))

        for i in range(vertex_count):
            xpoints[i] += (-(minx + maxx) / 2) + np.random.randint(0, image.shape[1])
            ypoints[i] += (-(miny + maxy) / 2) + np.random.randint(0, image.shape[0])

        # yy, xx
        return polygon(np.array(ypoints), np.array(xpoints), shape=mask.shape)

    def _augment_keypoints(self, keypoints_on_images, random_state, parents, hooks):
        return keypoints_on_images

    def get_parameters(self):
        return [self._poly, self._vertex]


class ColorTransfer(augmenters.Augmenter):
    """
    Source code at https://www.pyimagesearch.com/2014/06/30/super-fast-color-transfer-images/
    """
    _sources = dict()

    def __init__(self, images, name=None, deterministic=False, random_state=None):
        """
        Overlay the mean values of one image of the other.
        
        :param images: Dict of {str: images} from which to draw source images from. Checks the str before processing the image for duplicates. Use ColorTransfer.clear() to remove source archive.
        """
        super(ColorTransfer, self).__init__(name=name, deterministic=deterministic, random_state=random_state)
        assert type(images) is dict, 'images not of type dict'
        for img in images:
            if img not in ColorTransfer._sources:
                image = cv2.cvtColor(images[img], cv2.COLOR_BGR2LAB).astype("float32")
                ColorTransfer._sources[img] = ColorTransfer._image_stats(image)
        assert len(ColorTransfer._sources) > 0, 'source list is still empty'

    def _augment_images(self, images, random_state, parents, hooks):
        result = images
        nb_images = len(images)
        for i in range(nb_images):
            result[i] = self._color_transfer(images[i])
        return result

    @staticmethod
    def clear():
        ColorTransfer._sources = dict()

    @staticmethod
    def _image_stats(image):
        (l, a, b) = cv2.split(image)
        (lMean, lStd) = (l.mean(), l.std())
        (aMean, aStd) = (a.mean(), a.std())
        (bMean, bStd) = (b.mean(), b.std())

        # return the color statistics
        return lMean, lStd, aMean, aStd, bMean, bStd

    def _color_transfer(self, image):
        """Transfer the LAB colors from source image database onto the target image"""

        # source = cv2.cvtColor(source, cv2.COLOR_BGR2LAB).astype("float32")
        image = cv2.cvtColor(image, cv2.COLOR_BGR2LAB).astype("float32")

        (lMeanSrc, lStdSrc, aMeanSrc, aStdSrc, bMeanSrc, bStdSrc) = self._sources[
            np.random.choice(self._sources.keys())]
        (lMeanTar, lStdTar, aMeanTar, aStdTar, bMeanTar, bStdTar) = ColorTransfer._image_stats(image)

        # subtract the means from the target image
        (l, a, b) = cv2.split(image)
        l -= lMeanTar
        a -= aMeanTar
        b -= bMeanTar

        # scale by the standard deviations
        l = (lStdTar / lStdSrc) * l
        a = (aStdTar / aStdSrc) * a
        b = (bStdTar / bStdSrc) * b

        # add in the source mean
        l += lMeanSrc
        a += aMeanSrc
        b += bMeanSrc

        # clip the pixel intensities to [0, 255] if they fall outside
        # this range
        l = np.clip(l, 0, 255)
        a = np.clip(a, 0, 255)
        b = np.clip(b, 0, 255)

        # merge the channels together and convert back to the RGB color
        # space, being sure to utilize the 8-bit unsigned integer data
        # type
        transfer = cv2.merge([l, a, b])
        transfer = cv2.cvtColor(transfer.astype("uint8"), cv2.COLOR_LAB2BGR)

        # return the color transferred image
        return transfer

    def _augment_keypoints(self, keypoints_on_images, random_state, parents, hooks):
        return keypoints_on_images

    def get_parameters(self):
        return ColorTransfer._sources


class ObjectInsertion(augmenters.Augmenter):
    def __init__(self, images, locations, scales, name=None, deterministic=False, random_state=None):
        """
        :param images: List of images from which to draw insertable images from.
        :param locations: Dict of {keypad_number: chance}, where keypad_number is a value 0 - 9, chance is the chance of an object being inserted at location keypad_number (see keypad for a 3x3 grid). '0' means anywhere.
        :param scales: Float or tuple with length 2, such as (0.3, 0.5), meaning that inserted objects will be of size between 30% and 50% of background image.
        """
        super(ObjectInsertion, self).__init__(name=name, deterministic=deterministic, random_state=random_state)
        assert type(locations) is dict, 'locations not of type dict'
        assert len([x for x in locations if 0.0 < locations[x] <= 1.0 and 0 <= x <= 9]) == len(
            locations), 'some key(s) are not [0, 9], or some value(s) are not (0., 1.]'
        norm = sum(locations.values())
        self.locations = {x: locations[x] / norm for x in locations}

        assert type(scales) is float or type(scales) is tuple, 'scales not of type tuple or float'
        scales = [scales] if type(scales) is float else list(scales)
        self.scales = [min(scales), max(scales)]

        if type(images) is dict:
            images = images.values()

        assert type(images) is list, 'images not of type list'
        assert len(images) > 0, 'images is empty'
        self.images = images

    def _augment_images(self, images, random_state, parents, hooks):
        result = images
        nb_images = len(images)
        for i in range(nb_images):
            image = images[i]
            obj = self.images[np.random.choice(len(self.images))]
            obj_scale = (min(image.shape[:2]) * np.random.uniform(self.scales[0], self.scales[1])) / max(obj.shape[:2])
            obj = cv2.resize(obj, (0, 0), fx=obj_scale, fy=obj_scale)

            quad = [x / 3 for x in image.shape[:2]]
            keypad_trans = np.zeros((3, 3), dtype=tuple)
            for x in range(3):
                for y in range(3):
                    keypad_trans[x][y] = (quad[0] * x, quad[1] * y)
            keypad_trans = np.ndarray.flatten(np.flip(keypad_trans, 0))
            keypad_trans = {x + 1: keypad_trans[x] for x in range(9)}

            image_obj_loc = np.random.choice(self.locations.keys(), p=self.locations.values())
            if image_obj_loc == 0:
                image_obj_loc = np.random.randint(1, 10)

            yx = np.array(keypad_trans[image_obj_loc], dtype='float64')
            yx += [np.clip(np.random.normal(quad[x] / 2, quad[x] / 4), 0, quad[x]) for x in range(2)]

            y, x = yx.astype(dtype='int')
            x -= obj.shape[1] / 2
            y -= obj.shape[0]
            image = ObjectInsertion._overlay_transparent(image, obj, y, x)

            result[i] = image
        return result

    @staticmethod
    def _overlay_transparent(src, overlay, y, x):
        h, w, _ = overlay.shape
        rows, cols, _ = src.shape

        for i in range(h):
            for j in range(w):
                if y + i >= rows or y + i < 0 or x + j >= cols or x + j < 0:
                    continue
                alpha = float(overlay[i][j][3] / 255.0)  # read the alpha channel
                src[y + i][x + j] = alpha * overlay[i][j][:3] + (1 - alpha) * src[y + i][x + j]
        return src

    def _augment_keypoints(self, keypoints_on_images, random_state, parents, hooks):
        return keypoints_on_images

    def get_parameters(self):
        return None
