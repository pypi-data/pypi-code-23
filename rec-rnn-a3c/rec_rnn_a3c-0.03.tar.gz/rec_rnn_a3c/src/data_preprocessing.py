import csv
import json
import tempfile
import threading
import multiprocessing

import os

import boto3 as boto3
import pandas as pd
import tensorflow as tf
import botocore as botocore

from multiprocessing.pool import ThreadPool

from rec_rnn_a3c.src.util import replace_multiple, get_all_s3_keys, s3_download

DUMMY = True

S3 = boto3.client('s3')
BUCKET = 'rec-rnn-mpd'
#WORKING_DIR = tempfile.gettempdir()
WORKING_DIR = '/Users/Tim/Documents/mpd.v1'
DUMMY_FILENAMES = ["/Users/Tim/Documents/mpd.v1/data/mpd.slice.0-999.json"]

MAPPER = 'map_dummy' if DUMMY else 'map'
DATA = 'data_seq_dummy' if DUMMY else 'data_seq'

URI_TO_FREQUENCY = 'uri-to-frequency.csv'
URI_TO_ID = 'uri-to-id.csv'
ID_TO_URI = 'id-to-uri.csv'
PLAYLIST_DATAFRAME = 'playlist-dataframe.csv'


def calculate_mappers():
    def calculate_track_frequencies(file):
        if 'data' not in file:
            return {}

        with open(file) as json_raw:
            current_thread = threading.currentThread()

            print("Thread %s: Start processing file %s" % (current_thread, file))

            json_data = json.load(json_raw)
            data_frame = pd.DataFrame.from_dict(json_data['playlists'])

            all_playlist_tracks = {}
            for index, row in data_frame[['pid', 'tracks']].iterrows():
                pid = row['pid']
                playlist_tracks = row['tracks']
                df_playlist_tracks = pd.DataFrame(playlist_tracks)
                all_playlist_tracks[pid] = df_playlist_tracks

            uri_to_frequency = {}
            for pid, df_tracks in all_playlist_tracks.iteritems():
                for _, track_uri in df_tracks['track_uri'].iteritems():
                    if track_uri in uri_to_frequency:
                        uri_to_frequency[track_uri] += 1
                    else:
                        uri_to_frequency[track_uri] = 1
            print("Thread %s: Finished processing file %s" % (current_thread, file))
            return uri_to_frequency

    mapper_dir = os.path.join(WORKING_DIR, MAPPER)
    if not os.path.exists(mapper_dir):
        print("Created new dir %s" % mapper_dir)
        os.makedirs(mapper_dir)

    #if s3_download(S3, URI_TO_FREQUENCY, BUCKET, mapper_dir):
    #    print("Downloaded %s from S3 Bucket %s" % (URI_TO_FREQUENCY, BUCKET))

    uri_to_frequency_path = os.path.join(mapper_dir, URI_TO_FREQUENCY)
    try:
        with open(uri_to_frequency_path, 'rb') as f:
            print("Loaded %s successfully" % URI_TO_FREQUENCY)
            reader = csv.reader(f)
            uri_to_frequency = dict(reader)
    except IOError:
        print("Could not find %s - Now calculating..." % URI_TO_FREQUENCY)
        num_threads = multiprocessing.cpu_count()
        pool = ThreadPool(processes=num_threads)

        if not DUMMY:
            files = get_all_s3_keys(S3, BUCKET)
        else:
            files = DUMMY_FILENAMES

        results = pool.map(calculate_track_frequencies, files)
        pool.close()
        pool.join()

        uri_to_frequency = {}
        for mapper in results:
            for track_uri, frequency in mapper.iteritems():
                if track_uri in uri_to_frequency:
                    uri_to_frequency[track_uri] += frequency
                else:
                    uri_to_frequency[track_uri] = frequency

        with open(uri_to_frequency_path, 'wb') as f:
            writer = csv.writer(f)
            for key, value in uri_to_frequency.items():
                writer.writerow([key, value])
            print("Saved %s successfully" % URI_TO_FREQUENCY)

    sorted_uris = sorted(uri_to_frequency, key=uri_to_frequency.get)[::-1]


    #if s3_download(S3, URI_TO_ID, BUCKET, mapper_dir):
     #   print("Downloaded %s from S3 Bucket %s" % (URI_TO_ID, BUCKET))

    try:
        uri_to_id_path = os.path.join(mapper_dir, URI_TO_ID)
        test = open(uri_to_id_path, 'rb')
    except IOError:
        print("Could not find %s - Now calculating..." % URI_TO_ID)

        uri_to_id = {}
        for idx, uri in enumerate(sorted_uris):
            uri_to_id[uri] = idx

        uri_to_id_path = os.path.join(mapper_dir, URI_TO_ID)
        with open(uri_to_id_path, 'wb') as f:
            writer = csv.writer(f)
            for key, value in uri_to_id.items():
                writer.writerow([key, value])
        print("Saved %s successfully" % URI_TO_ID)


def calculate_dataset():
    def make_example(sequence, labels):
        # The object we return
        ex = tf.train.SequenceExample()
        # A non-sequential feature of our example
        # sequence_length = len(sequence)
        # ex.context.feature["length"].int64_list.value.append(sequence_length)
        # Feature lists for the two sequential features of our example
        fl_tokens = ex.feature_lists.feature_list["train/sequence"]
        fl_labels = ex.feature_lists.feature_list["train/labels"]
        for token, label in zip(sequence, labels):
            fl_tokens.feature.add().int64_list.value.append(token)
            fl_labels.feature.add().int64_list.value.append(label)
        return ex

    def convert_to_tfrecords(file):
        if 'data' not in file:
            return

        current_thread = threading.currentThread()
        print("Thread %s: Start processing file %s" % (current_thread, file))

        file_path = os.path.join(WORKING_DIR, file)
        conv_file_path = replace_multiple(file_path, {'data': DATA, 'json': 'tfrecords'})

        if os.path.isfile(conv_file_path):
            print("Thread %s: Converted file %s already exists." % (current_thread, file))
        else:
            dir, _ = os.path.split(file_path)
            if not os.path.exists(dir):
                os.makedirs(dir)

            if not os.path.isfile(file_path):
                try:
                    S3.download_file(BUCKET, file, file_path)
                except botocore.exceptions.ClientError as e:
                    if e.response['Error']['Code'] == "404":
                        print("Thread %s: File %s does not exist in S3." % (current_thread, file))
                    else:
                        raise

            with open(file_path) as json_raw:
                json_data = json.load(json_raw)
                data_frame = pd.DataFrame.from_dict(json_data['playlists'])

                sequences = []
                label_sequences = []
                for index, row in data_frame[['pid', 'tracks']].iterrows():
                    playlist_tracks = row['tracks']

                    seq = [uri_to_id[t['track_uri']] for t in playlist_tracks]
                    sequences.append(seq[:-1])
                    label_sequences.append(seq[1:])

                dir, _ = os.path.split(conv_file_path)
                if not os.path.exists(dir):
                    print("Thread %s: Created new dir %s" % (current_thread, dir))
                    os.makedirs(dir)
                with open(conv_file_path, 'wb') as fp:
                    writer = tf.python_io.TFRecordWriter(fp.name)
                    for sequence, label_sequence in zip(sequences, label_sequences):
                        ex = make_example(map(int, sequence), map(int, label_sequence))
                        writer.write(ex.SerializeToString())
                    writer.close()
                    print('Thread %s: Saved file %s ...' % (current_thread, conv_file_path))

    if not DUMMY:
        files = get_all_s3_keys(S3, BUCKET)
    else:
        files = DUMMY_FILENAMES

    mapper_dir = os.path.join(WORKING_DIR, MAPPER)
    if s3_download(S3, URI_TO_ID, BUCKET, mapper_dir):
        print("Downloaded %s from S3 Bucket %s" % (URI_TO_ID, BUCKET))

    uri_to_id_path = os.path.join(mapper_dir, URI_TO_ID)
    with open(uri_to_id_path, 'rb') as csv_file:
        print("Loaded %s successfully" % URI_TO_ID)

        reader = csv.reader(csv_file)
        uri_to_id = dict(reader)

    for _ in files:
        num_threads = multiprocessing.cpu_count()
        pool = ThreadPool(processes=num_threads)
        pool.map(convert_to_tfrecords, files)
        pool.close()


if __name__ == "__main__":
    calculate_mappers()
    calculate_dataset()




