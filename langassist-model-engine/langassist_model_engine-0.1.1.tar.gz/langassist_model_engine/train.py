import argparse
import logging

from sklearn import preprocessing
from sklearn.model_selection import train_test_split

from langassist_model_engine.native_lang_identification.data import prep_data
from langassist_model_engine.native_lang_identification.model.base import BaseModel
from langassist_model_engine.native_lang_identification.model import logireg
from langassist_model_engine.nlp_utils.features.builders.get_builder import get_builder

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s:\t %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

def parse_args():
    '''
        Argument Parsing
    '''
    parser = argparse.ArgumentParser(description='''For training models''')
    parser.add_argument('--model', '-m',
                        help="The model to train. Currently only 'nli'",
                        type=str,
                        default='nli',
                        metavar="MODEL")
    parser.add_argument('--feature-builder', '-fb',
                        help="Feature Builder to use (vocab, hash)",
                        type=str,
                        default='hash',
                        metavar='FEAT-BUILDER')
    parser.add_argument('--num-samples',
                        help='The number of samples to use. 0 is default and means "use all"',
                        type=int,
                        default=0,
                        metavar="NUM_SAMPLES")
    parser.add_argument('--n-features',
                        help="Maximum number of features for (vocab model only)",
                        type=int,
                        default=0,
                        metavar="N_FEATURES")
    parser.add_argument('--produce-graphs', '-g',
                        action='store_true',
                        help="Specify whether or not to produce graphs",
                        default=False)
    parser.add_argument('--latest', '-l',
                        action='store_true',
                        help="Specify whether or not this model will be the current latest version",
                        default=False)
    parser.add_argument('--test', '-t',
                        action='store_true',
                        help="Specify whether or not to test the model using a test/train split",
                        default=False)
    parser.add_argument('--prod', '-p',
                        action='store_true',
                        help="Specify whether or not the model is intended for production use",
                        default=False)
    parser.add_argument('--word-ngram-range', '-wnr',
                        help='Specify the range for word n-grams',
                        nargs=2,
                        default=(1, 3),
                        metavar="W_NGRAM")
    parser.add_argument('--char-ngram-range', '-cnr',
                        help='Specify the range for char n-grams',
                        nargs=2,
                        default=(3, 7),
                        metavar="C_NGRAM")
    parser.add_argument('--to-pickle', '-tp',
                        help="Whether or not to save the model to a pickle",
                        action='store_true',
                        default=True)
    parser.add_argument('--from-pickle', '-fp',
                        help="Whether or not to load the model from a pickle",
                        type=str,
                        default="")

    return parser.parse_args()

def _ngr_to_int(ngr):
    '''
        Turn a tuple of str into a tuple of int.
        For cmd line parsing
    :param ngr:
    :return:
    '''
    # ngr means n-gram-range
    # TODO change ngr to something that will make sense when I read this again in 2 months
    return (int(ngr[0]), int(ngr[1]))

def train(opts):
    '''
        Train the required model, parameterised by the command line options
    :param opts:
    :return:
    '''
    logger.info("Preparing training data...")
    doc_data, s_data = prep_data.get_training_data(opts.num_samples)
    # Sentence labels
    Y_train = s_data['l1']
    logger.debug("%s unique labels" % Y_train.nunique())
    s_data = s_data.drop('l1', axis=1)

    min_max_scaler = preprocessing.MaxAbsScaler()  # Used to normalise data between 0 and 1

    if(opts.from_pickle is not ""):
        dir, key = opts.from_pickle.split('/')
        model = BaseModel.load(dir, key)
        feature_builder = model.feature_builder
    else:
        logger.info("Constructing feature builder and scaler...")
        # Get the requested feature builder class and then instantiate it
        fb_cls = get_builder(opts.feature_builder)
        feature_builder = fb_cls(_ngr_to_int(opts.word_ngram_range), _ngr_to_int(opts.word_ngram_range))
        model = logireg.LogiReg(feature_builder)
        # Encode string labels as integers
        model.fit_label_encoder(Y_train)

    logger.info("Featurizing data...")
    X_train = feature_builder.featurize_all(s_data.values.ravel())

    if(opts.test):
        X_train, x_test, Y_train, y_test = train_test_split(X_train, Y_train, test_size=0.9, random_state=42)

        X_train = min_max_scaler.fit_transform(X_train)
        x_test = min_max_scaler.fit_transform(x_test)

        model.train(X_train, Y_train)
        model.test(x_test, y_test)
    else:
        X_train = min_max_scaler.fit_transform(X_train)
        model.train(X_train, Y_train)

    if(opts.to_pickle):
        model.save(opts.prod, latest=opts.latest)


if __name__ == "__main__":
    train(parse_args())