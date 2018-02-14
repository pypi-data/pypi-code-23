import csv

import numpy as np
import pandas as pd

df = pd.read_csv("/data/SSCAIT_2017/results_within_timelimit.csv")
bots = set(df['bot_0']).union((set(df['bot_1'])))

mask = df['winner_player'] == 0
swp = df[mask]['bot_0'].tolist()
df.loc[mask, 'bot_0'] = df[mask]['bot_1'].copy()
df.loc[mask, 'bot_1'] = swp
df['winner_player'] = 1

df_res = pd.pivot_table(df, index='bot_0', columns='bot_1', values='winner_player', aggfunc=np.sum)
df_times = pd.pivot_table(df, index='bot_0', columns='bot_1', values='game_time', aggfunc=np.sum)
df_res = df_res.fillna(0)
df_res = df_res.sort_index()
df_res = df_res.transpose()

df_times = df_times.fillna(0)
df_times = ((df_times + df_times.transpose())) / ((df_res + df_res.transpose()))

df_timeouts = df_res + df_res.transpose()

df_res.to_csv("results.csv", quoting=csv.QUOTE_MINIMAL, sep="\t")
df_times.to_csv("results_times.csv", quoting=csv.QUOTE_MINIMAL, sep="\t")
df_timeouts.to_csv("results_timeout.csv", quoting=csv.QUOTE_MINIMAL, sep="\t")
print(df_res.shape)
