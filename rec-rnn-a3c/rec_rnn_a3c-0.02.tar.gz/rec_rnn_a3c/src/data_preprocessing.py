import csv
import multiprocessing
import threading
from multiprocessing.pool import ThreadPool

import os
import json
import pandas as pd
import glob

URI_TO_FREQUENCY = 'uri-to-frequency.csv'
PLAYLIST_DATAFRAME = 'playlist-dataframe.csv'
VERBOSE = False

filenames = glob.glob("/Users/Tim/Documents/mpd.v1/data/*.json")
#filenames = ["/Users/Tim/Documents/mpd.v1/data/mpd.slice.0-999.json", "/Users/Tim/Documents/mpd.v1/data/mpd.slice.1000-1999.json"]


def calculate_track_frequencies(file):
    with open(file) as json_raw:
        current_thread = threading.currentThread()

        print("Thread %s starting for file %s" % (current_thread, file))

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

        return uri_to_frequency


try:
    with open(URI_TO_FREQUENCY, 'rb') as csv_file:
        print("%s found!" % URI_TO_FREQUENCY)
        reader = csv.reader(csv_file)
        uri_to_frequency = dict(reader)
except IOError:
    print("%s not found - calculating..." % URI_TO_FREQUENCY)
    num_threads = multiprocessing.cpu_count()
    pool = ThreadPool(processes=num_threads)
    results = pool.map(calculate_track_frequencies, filenames)
    pool.close()
    pool.join()

    uri_to_frequency = {}
    for mapper in results:
        for track_uri, frequency in mapper.iteritems():
            if track_uri in uri_to_frequency:
                uri_to_frequency[track_uri] += frequency
            else:
                uri_to_frequency[track_uri] = frequency

    with open(URI_TO_FREQUENCY, 'wb') as csv_file:
        writer = csv.writer(csv_file)
        for key, value in uri_to_frequency.items():
            writer.writerow([key, value])

try:
    concatenated_playlist_tracks = pd.read_csv(os.path.join(PLAYLIST_DATAFRAME), index_col=[0, 1])
    print("%s found!" % PLAYLIST_DATAFRAME)

except IOError:
    print("%s not found - calculating..." % PLAYLIST_DATAFRAME)
    sorted_uris = sorted(uri_to_frequency, key=uri_to_frequency.get)[::-1]

    uri_to_id = {}
    for idx, uri in enumerate(sorted_uris):
        uri_to_id[uri] = idx

    id_to_uri = {y: x for x, y in uri_to_id.iteritems()}

    verbose_playlist_tracks = {}
    reduced_playlist_tracks = {}
    filenames = ["/Users/Tim/Documents/mpd.v1/data/mpd.slice.0-999.json", "/Users/Tim/Documents/mpd.v1/data/mpd.slice.1000-1999.json"]
    for file in filenames:
        with open(file) as json_raw:
            json_data = json.load(json_raw)
            data_frame = pd.DataFrame.from_dict(json_data['playlists'])

            for index, row in data_frame[['pid', 'tracks']].iterrows():
                pid = row['pid']
                playlist_tracks = row['tracks']
                df_playlist_tracks = pd.DataFrame(playlist_tracks)
                verbose_playlist_tracks[pid] = df_playlist_tracks

            for pid, df_tracks in verbose_playlist_tracks.iteritems():
                track_ids = []
                for _, track_uri in df_tracks['track_uri'].iteritems():
                    track_ids.append(uri_to_id[track_uri])

                reduced_playlist_tracks[pid] = track_ids
                verbose_playlist_tracks[pid] = df_tracks.assign(track_id=track_ids)


    # TODO: Make this nicer
    if VERBOSE:
        concatenated_playlist_tracks = pd.concat(verbose_playlist_tracks)
        concatenated_playlist_tracks.to_csv(os.path.join(PLAYLIST_DATAFRAME), encoding='utf-8')
    else:
        with open(PLAYLIST_DATAFRAME, 'wb') as csv_file:
            writer = csv.writer(csv_file)
            for key, value in reduced_playlist_tracks.items():
                writer.writerow([key, value])

batch_dim = 1
length = concatenated_playlist_tracks.index.get_level_values(0).max() + 1
num_epochs = length // batch_dim

sequenced_item_data = concatenated_playlist_tracks['track_id']

for i in range(num_epochs):
    sample_item_data = sequenced_item_data.loc[(i*batch_dim):((i+1)*batch_dim)].values
    print(sample_item_data)


