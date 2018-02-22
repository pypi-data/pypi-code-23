from keras.models import Sequential
from keras.layers import Activation, LSTM
from adlframework.nets.net import Net
import attr

@attr.s
class medium_image_vae(Net):
    @Net.build_model_wrapper
    def build_model(self, mode=False):
        model = Sequential()
        model.add(LSTM(32, name="lstm_1", input_shape=self.shape, return_sequences=True))
        # model.add(Dropout(rate=0.7))
        model.add(LSTM(64, name="lstm_2", return_sequences=True))
        model.add(LSTM(128, name="lstm_3", return_sequences=True))
        # model.add(LSTM(32, name="lstm_4", return_sequences=True))
        model.add(LSTM(2, name = 'planet_lstm_output'))
        model.add(Activation('softmax', name = 'planet_other_activation'))
        return model