from vaisdemo.Truecaser import *
import pickle
import os
import string

uniDist = None
backwardBiDist = None
forwardBiDist = None
trigramDist = None
wordCasingLookup = None

def evaluateTrueCaser(sentence):
    if not uniDist:
        return sentence
    correctTokens = 0
    totalTokens = 0

    tokensCorrect = sentence.lower().split()
    tokens = [token for token in tokensCorrect]
    tokensTrueCase = getTrueCase(tokens, 'title', wordCasingLookup, uniDist, backwardBiDist, forwardBiDist, trigramDist)

    return " ".join(tokensTrueCase)

def load_model():
    global uniDist, backwardBiDist, forwardBiDist, trigramDist, wordCasingLookup
    root_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(root_dir, 'distributions.obj')
    if file_path:
        f = open(file_path, 'rb')
        wordCasingLookup = pickle.load(f)
        uniDist = pickle.load(f)
        backwardBiDist = pickle.load(f)
        forwardBiDist = pickle.load(f)
        # trigramDist = pickle.load(f)
        # trigramDist = None
        f.close()
