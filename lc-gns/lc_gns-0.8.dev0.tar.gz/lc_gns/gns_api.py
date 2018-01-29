
import numpy as np
import random
from PIL import Image
from gns import GNS



class GNS_api(object):
    def gns(self, digits, spacing_range, image_width):
        img_data = (GNS().generate_numbers_sequence(digits, spacing_range, image_width)* 255.0).astype(np.uint8)
        return img_data
    def save_img(self, img_data, digits):
        gns_image = Image.fromarray(img_data)
        img_name = "-".join(list(map(str, digits)))
        gns_image.save(img_name + ".png")
        print("\n Success: Digit sequence " + img_name +
              " as image is generated and saved as " + img_name + ".png\n")
