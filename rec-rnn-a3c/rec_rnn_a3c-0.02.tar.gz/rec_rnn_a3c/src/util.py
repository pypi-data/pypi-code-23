import os
import csv
import boto3
import botocore
import scipy.signal

import numpy as np
import pandas as pd
import tensorflow as tf

from copy import deepcopy
from botocore import UNSIGNED
from botocore.config import Config


def update_target_graph(from_scope, to_scope):
    from_vars = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, from_scope)
    to_vars = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, to_scope)

    op_holder = []
    for from_var, to_var in zip(from_vars, to_vars):
        op_holder.append(to_var.assign(from_var))
    return op_holder


def normalized_columns_initializer(std=1.0):
    def _initializer(shape, dtype=None, partition_info=None):
        out = np.random.randn(*shape).astype(np.float32)
        out *= std / np.sqrt(np.square(out).sum(axis=0, keepdims=True))
        return tf.constant(out)
    return _initializer


def discount(x, gamma):
    return scipy.signal.lfilter([1], [1, -gamma], x[:, ::-1], axis=1)[:, ::-1]  # x[::-1] reverses x


def generate_spotify_placeholder_input_fn(batch_dim):
    def _input_fn():
        file_path = os.path.split(os.getcwd())[0] + '/src/playlist-dataframe.csv'
        with open(file_path, 'rb') as csv_file:
            print("%s found!" % file_path)
            reader = csv.reader(csv_file)
            playlists = dict(reader)

        length = len(playlists)
        num_epochs = length // batch_dim

        for i in range(num_epochs):
            sample_item_data = eval(playlists[str(i)])

            features_i = deepcopy(sample_item_data)
            features_i.pop()
            features_i = pd.DataFrame(features_i, dtype=int)
            features_i = features_i.fillna(0).values.astype(int)

            labels = deepcopy(sample_item_data)
            labels.pop(0)
            labels = pd.DataFrame(labels, dtype=int)
            labels = labels.fillna(0).values.astype(int)

            features = {
                'user': [],
                'item': np.reshape(features_i, newshape=[batch_dim, -1])
            }

            yield features, {'item': np.reshape(labels, newshape=[batch_dim, -1])}

    return _input_fn


def generate_placeholder_input_fn(batch_dim, data=None, file_pattern=None, easymode=False):
    def _input_fn():
        if file_pattern is not None:
            user_data, item_data = [], []
            with open(file_pattern) as f:
                for line in f.readlines():
                    (user, item) = line.rstrip().split(',')
                    user_data.append(int(user))
                    item_data.append(int(item))
        elif data is not None:
            user_data, item_data = data['user'], data['item']
        else:
            raise ValueError('Either data or file_pattern have to be different from None')
        item_data = np.array(item_data, dtype=np.int32)
        user_data = np.array(user_data, dtype=np.int32)

        user_ids, user_indices, user_lengths = np.unique(user_data, return_index=True, return_counts=True)

        sequenced_user_data, sequenced_item_data, sequenced_target_data = [], [], []
        for i in range(len(user_ids)):
            # Cut off the last element because we have no target here
            if user_lengths[i] > 1:
                sequenced_user_data.append(user_data[user_indices[i]:user_indices[i]+user_lengths[i] - 1])
                sequenced_item_data.append(item_data[user_indices[i]:user_indices[i]+user_lengths[i] - 1])
                sequenced_target_data.append(item_data[user_indices[i]+1:user_indices[i]+user_lengths[i]])

        num_epochs = len(sequenced_item_data) // batch_dim

        i = 0
        for _ in range(num_epochs):
            if easymode:
                i = num_epochs // 2
            else:
                i = np.random.randint(0, num_epochs)

            i = _
            labels = sequenced_target_data[i*batch_dim:(i+1)*batch_dim]
            features_i = sequenced_item_data[i*batch_dim:(i+1)*batch_dim]
            features_u = sequenced_user_data[i*batch_dim:(i+1)*batch_dim]

            features_i = pd.DataFrame(features_i, dtype=int)
            features_i = features_i.fillna(0).values.astype(int)

            features_u = pd.DataFrame(features_u, dtype=int)
            features_u = features_u.fillna(0).values.astype(int)

            labels = pd.DataFrame(labels, dtype=int)
            labels = labels.fillna(0).values.astype(int)

            features = {
                'user': features_u,
                'item': features_i
            }

            yield features, {'item': labels}

    return _input_fn

def maybe_download(bucket, dir, files):
    paths = {}
    s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))

    for f in files:
        file_path = os.path.join(dir, f)
        if not os.path.isfile(file_path):
            try:
                s3.download_file(bucket, f, file_path)
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == "404":
                    print("The object does not exist.")
                else:
                    raise
        paths[f] = file_path

    return paths