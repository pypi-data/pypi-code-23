from sklearn.linear_model import LogisticRegression

from native_lang_identification.model.base import BaseModel


class SS_Model(BaseModel):
    def __init__(self, train_x, train_y):
        BaseModel.__init__(self)
        self.model = LogisticRegression()

    def train(self, train_x, train_y):
        pass

    def test(self, test_x, test_y):
        pass

    def predict(self, predict_x):
        pass




