# coding: utf-8
import numpy as np
import random
import warnings
warnings.filterwarnings("ignore")
# use this import to ignore the non-fatal FutureWarning from keras h5py.

from keras.datasets import mnist
# import pre-proccessed mnist dataset with labels and images mapped.

(x_train, y_train), (x_test, y_test) = mnist.load_data()
# (x_train,y_train) are the (images,labels) respectively in the mnist training set.

x_train = x_train.astype('float32')
x_train /= 255
# Images are converted to float32 with each pixels ranging from
# 0(black)-1(white).


class GNS(object):

    def calculate_space_between_digits(self, len_seq, min_spacing, max_spacing,
                                       output_width, DIGIT_WIDTH=28):
        # check if single digit is passed in --seq args.
        if len_seq <= 1:
            print("Only single digit passed into arguments, " +
                  "try passing more than one to build a sequence.")
            return 0

        else:
            # if more than one digit is passed in --seq then continue to
            # calculate spacing.
            calc_spacing = (output_width - len_seq *
                            DIGIT_WIDTH) / ((len_seq - 1) * 1.0)

       # Suggestions: changes to be made in max_width(--width) or (min_spacing,max_spacing)(--space) are suggested
            # if in case the sequence image cannot be generated with the given parameters.

            if not calc_spacing.is_integer() or calc_spacing < min_spacing or calc_spacing > max_spacing:
                print(
                    "\nAs uniform spacing is not possible for the given set of values," +
                    " try these suggestions :")

                # if calc_spacing is not an integer suggest the next nearest
                # max_width.
                if not calc_spacing.is_integer() and calc_spacing > 0:

                    # calculate the next nearest image_width(--width) to
                    # suggest.
                    output_width = int(
                        calc_spacing) * ((len_seq - 1) * 1.0) + len_seq * DIGIT_WIDTH

                    print (" Choose output_image_width = " + str(int(output_width)) + " for " \
                        + str(int(calc_spacing)) + "px space bewteen digits.\n")

                # suggest the max_spacing value.
                if calc_spacing > max_spacing:
                    print (" Choose max spacing value >= " + str(int(calc_spacing)) + ".\n")

                # suggest the min_spacing value.
                if calc_spacing < min_spacing and calc_spacing >= 0:
                    print (" Choose min spacing value <= " + str(int(calc_spacing)) \
                        + " or try increasing output image width.\n")

                # if calc_spacing is <0 the digits images overlap or cannot be
                # generated.
                if calc_spacing < min_spacing and calc_spacing < 0:
                    print (" Digits images overlapped. " + \
                        "Given output image width should be greater than " + str(int(len_seq) * 28) + ".\n\n")

                exit()

            # return calc_spacing when space >=0 can generated with given parameters.
            return int(calc_spacing)
        

    def get_digits_image_from_mnist(self, digits):
        # iterate through mnist x_train using y_train labels and load seq. into
        # image_arr[]
        image_arr = []
        for digit in digits:
            indices = [i for i, x in enumerate(y_train) if x == digit]

        # choose digit image randomly from one of its representations in the
        # MNIST dataset.
            image = x_train[random.sample(set(indices), 1)[0]]
            image_arr.append(image)

        # return array of randomly loaded representations of digit images.
        return image_arr
    

    def gen_image(self, digits_seqs, calc_space):

        digits_img_seq = self.get_digits_image_from_mnist(digits_seqs)

        # create a single blank_space image.
        blank_space = np.zeros((28, calc_space)).astype('float32')
        space = [blank_space]

        # create a blank output_image of given width.
        output = space * (2 * (len(digits_img_seq)) - 1)

        # place digit images from array at every alternate positions into the
        # blank output_image.
        for i in range(0, len(digits_img_seq)):
            output[0::2] = digits_img_seq  # i.e digit,space,digit,space,digit.

        vis = np.concatenate((output), axis=1)
        return vis  # return stitched image array.

    
    def generate_numbers_sequence(self, digits, spacing_range, image_width):

        # check if --seq digits are >=0 and <=9 i.e[0-9]
        if all(i <= 9 and i >= 0 for i in digits):
            digit_spacing = self.calculate_space_between_digits(
                len(digits),
                spacing_range[0],
                spacing_range[1],
                image_width)
            out = self.gen_image(digits, digit_spacing)
            return out #return output image np.array
        else:
            print ('\n\nAlert: Choose sequence digits between 0-9!')
            print ('       Check input arguments at --seq ' + str(digits).strip('[').strip(']') + ' \n\n')
            exit()  # exit if --seq does not lie between [0-9]
