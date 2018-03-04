import pandas as pd

from langassist_model_engine.constants import DATA_ROOT, NLI_DEV, DATA_FORMAT
from langassist_model_engine.nlp_utils.tokenize import *

####################
###  Load Files  ###
####################

def load_csv(file_name, num_samples):
    if(num_samples == 0):
        return pd.read_csv(file_name, delimiter=',')
    return pd.read_csv(file_name, delimiter=',').sample(num_samples)

def load_file(file):
    with open(file) as f:
        return f.read()

##########################
###  Build File Names  ###
##########################

def build_index_file_name(index_name):
    return ''.join((DATA_ROOT, index_name))

def build_data_file_name(data_name):
    return ''.join((DATA_ROOT, "responses/", DATA_FORMAT, data_name))

###########################
###  Build Data Frames  ###
###########################

def load_total_data(index_file, num_samples):
    ind_df = load_csv(build_index_file_name(index_file), num_samples)

    ind_df['Filename'] = ind_df['Filename'].apply(lambda x: load_file(build_data_file_name(x)))


    return ind_df

def get_sentence_pairs(doc_pairs):
    sent_pairs = pd.DataFrame(columns=['sentence', 'l1'])
    for index, row in doc_pairs.iterrows():
        l1 = row['l1']
        sentences = to_sentences(row['document'])
        for s in sentences:
            sent_pairs = sent_pairs.append({'sentence': s, 'l1': l1}, ignore_index=True)

    return sent_pairs

###############################
###  Prepare Training Data  ###
###############################

def get_training_data(num_samples):
    document_pairs = load_total_data(NLI_DEV, num_samples)
    document_pairs = document_pairs.rename(columns={'Filename': 'document', 'Language': 'l1'})
    document_pairs = document_pairs[['document', 'l1']]
    sentence_pairs = get_sentence_pairs(document_pairs)

    return document_pairs, sentence_pairs