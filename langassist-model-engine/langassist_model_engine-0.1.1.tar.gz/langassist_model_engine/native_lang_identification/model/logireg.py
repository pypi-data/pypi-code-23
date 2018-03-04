import logging

import numpy as np
from sklearn import preprocessing
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score

from langassist_model_engine.native_lang_identification.model.base import BaseModel

logger = logging.getLogger(__name__)

class LogiReg(BaseModel):
    '''
    A wrapper class around Logistic Regression
    '''
    def __init__(self, feature_builder):
        BaseModel.__init__(self, feature_builder)
        self.le = preprocessing.LabelEncoder()
        self.model = LogisticRegression(penalty="l2", C=1.0)


    def fit_label_encoder(self, labels):
        logger.debug("Fitting labels to encoder...")
        self.le.fit(labels)

    def train(self, x_train, y_train):
        logger.info("Training...")
        self.model.fit(x_train, y_train)

    def test(self, x_test, y_test):
        logger.info("Testing...")
        preds = self.model.predict(x_test)

        scores = cross_val_score(self.model, x_test, y_test, cv=5)

        logger.info("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))

        # encoded_y = self.le.transform(y_test)
        # encoded_preds = self.le.transform(preds)
        #
        # for i, j in zip(preds, y_test):
        #     logger.debug("Expected %s, Guessed %s" % (j, i))
        #
        # logger.debug("Mean squared error: %.2f"
        #       % mean_squared_error(encoded_y, encoded_preds))
        # logger.debug("LogRegr .score(): %s" % self.model.score(x_test, y_test))
        # logger.info("F1 Score: %s" % f1_score(encoded_y, encoded_preds, average="micro"))

    def predict(self, predict_x):
        probs = self.model.predict_proba(predict_x)
        confidence = max(probs[0])
        res_index = np.argmax(probs[0])
        prediction = self.le.classes_[res_index]

        return (prediction, confidence)
