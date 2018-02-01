#!/usr/bin/env python
import os
import pickle
import argparse
import pandas as pd
from genomeqaml import extract_features


def classify_data(model, test_folder, refseq_database):
    # Extract features from the training folder.
    if not os.path.isfile(os.path.join(test_folder, 'extracted_features.csv')):
        extract_features.main(sequencepath=test_folder,
                              report=True,
                              refseq_database=refseq_database)
    test_df = pd.read_csv(os.path.join(test_folder, 'extracted_features.csv'))
    dataframe = pd.get_dummies(test_df, columns=['Genus'], dummy_na=True)
    df = pickle.load(open('../dataframe.p', 'rb'))
    training_dataframe = pd.get_dummies(df, columns=['Genus'], dummy_na=True)
    for column in dataframe:
        if column not in training_dataframe:
            dataframe.drop(column, axis=1, inplace=True)
    # Add any genera that weren't in our test set but were in the training set.
    for column in training_dataframe:
        if 'Genus' in column and column not in dataframe:
            not_present = [0] * len(dataframe)
            dataframe[column] = not_present
    # Then, add any features that were part of training data but not part of test data
    features = list(dataframe.columns[1:len(dataframe.columns)])
    x = dataframe[features]
    result = model.predict(x)
    # result = tree.predict_proba(x)
    for i in range(len(result)):
        if result[i] == 0:
            output = 'Fail'
        elif result[i] == 1:
            output = 'Pass'
        elif result[i] == 2:
            output = 'Reference'
        print(test_df['SampleName'][i] + ',' + output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--test_folder',
                        type=str,
                        required=True,
                        help='Path to folder containing FASTA files you want to test.')
    args = parser.parse_args()
    model = pickle.load(open('../model.p', 'rb'))
    classify_data(model, args.test_folder, '../refseq.msh')
