import os
import pickle


def load_cached(filename, do_unless_found):
    if not os.path.isfile(filename):
        values = do_unless_found()
        with open(filename, "wb") as pickle_out:
            pickle.dump(values, pickle_out)

    with open(filename, "rb") as pickle_in:
        return pickle.load(pickle_in)
