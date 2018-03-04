from nlp_utils.features.builders import vocab_featurizer, hash_featurizer

def get_builder(builder_name):
    if(builder_name == "vocab"):
        return vocab_featurizer.VocabFeaturizer
    elif(builder_name == "hash"):
        return hash_featurizer.HashFeaturizer