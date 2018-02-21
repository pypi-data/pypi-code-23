from keras.layers import Input, Conv2D, Dense, MaxPool2D, UpSampling2D
from keras.layers import Dropout, Flatten
from keras.models import Model
from keras import backend

_CHANNEL_AXIS = 1 if backend.image_data_format() == "channels_first" else -1

_VGG19_FORWARD_LAYERS = [
    Conv2D(64, (3, 3), padding='same', activation='relu'),
    Conv2D(64, (3, 3), padding='same', activation='relu'),
    MaxPool2D(),
    Conv2D(128, (3, 3), padding='same', activation='relu'),
    Conv2D(128, (3, 3), padding='same', activation='relu'),
    MaxPool2D(),
    Conv2D(256, (3, 3), padding='same', activation='relu'),
    Conv2D(256, (3, 3), padding='same', activation='relu'),
    Conv2D(256, (3, 3), padding='same', activation='relu'),
    Conv2D(256, (3, 3), padding='same', activation='relu'),
    MaxPool2D(),
    Conv2D(512, (3, 3), padding='same', activation='relu'),
    Conv2D(512, (3, 3), padding='same', activation='relu'),
    Conv2D(512, (3, 3), padding='same', activation='relu'),
    Conv2D(512, (3, 3), padding='same', activation='relu'),
    MaxPool2D(),
    Conv2D(512, (3, 3), padding='same', activation='relu'),
    Conv2D(512, (3, 3), padding='same', activation='relu'),
    Conv2D(512, (3, 3), padding='same', activation='relu'),
    Conv2D(512, (3, 3), padding='same', activation='relu'),
    MaxPool2D(),
]

_VGG19_BACKWARD_LAYERS = [
    Conv2D(512, (3, 3), padding='same', activation='relu'),
    Conv2D(512, (3, 3), padding='same', activation='relu'),
    Conv2D(512, (3, 3), padding='same', activation='relu'),
    Conv2D(512, (3, 3), padding='same', activation='relu'),
    UpSampling2D(),
    Conv2D(512, (3, 3), padding='same', activation='relu'),
    Conv2D(512, (3, 3), padding='same', activation='relu'),
    Conv2D(512, (3, 3), padding='same', activation='relu'),
    Conv2D(512, (3, 3), padding='same', activation='relu'),
    UpSampling2D(),
    Conv2D(256, (3, 3), padding='same', activation='relu'),
    Conv2D(256, (3, 3), padding='same', activation='relu'),
    Conv2D(256, (3, 3), padding='same', activation='relu'),
    Conv2D(256, (3, 3), padding='same', activation='relu'),
    UpSampling2D(),
    Conv2D(128, (3, 3), padding='same', activation='relu'),
    Conv2D(128, (3, 3), padding='same', activation='relu'),
    UpSampling2D(),
    Conv2D(64, (3, 3), padding='same', activation='relu'),
    Conv2D(64, (3, 3), padding='same', activation='relu'),
    UpSampling2D(),
]

class UniversalStyleTransfer(object):
    """docstring for UniversalStyleTransfer."""
    def __init__(self, input_shape=(224, 224, 3)):
        super(UniversalStyleTransfer, self).__init__()
        self._input_shape = input_shape
        self._model = None
        self._encoder = None
        self._decoder = None
        self._bottleneck = None

    def build_model(self):
        _input = Input(self._input_shape)

        # Encoder
        self._encoder = _input
        for layer in _VGG19_FORWARD_LAYERS:
            self._encoder = layer(self._encoder)

        # Save ref to bottleneck layer
        self._bottleneck = self._encoder

        # Decoder
        self._decoder = self._bottleneck
        for layer in _VGG19_BACKWARD_LAYERS:
            self._decoder = layer(self._decoder)

        _output = self._decoder

        self._model = Model(inputs=_input, outputs=_output)
        return self._model

    def whitening_transform(self):
        pass

    def coloring_transform(self):
        pass

    def encode_img(self, img):
        pass

    def decode_img(self, img):
        pass

    def style_transfer(self, content_img, style_img, alpha=0.5):
        pass


if __name__ == '__main__':
