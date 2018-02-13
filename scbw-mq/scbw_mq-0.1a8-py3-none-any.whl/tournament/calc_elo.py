from pprint import pprint

import numpy as np
import pandas as pd
import elo
from tqdm import tqdm

ratings = dict()


#: The actual score for win.
WIN = 1.
#: The actual score for draw.
DRAW = 0.5
#: The actual score for loss.
LOSS = 0.

#: Default K-factor.
K_FACTOR = 20
#: Default rating class.
RATING_CLASS = float
#: Default initial rating.
INITIAL = 2000
#: Default Beta value.
BETA = 200


df = pd.read_csv("/data/SSCAIT_2017/results_within_timelimit.csv")
bots = set(df['bot_0']).union((set(df['bot_1'])))
ratings = {bot: elo.CountedRating(INITIAL) for bot in bots}

elo_calc = elo.Elo(
    k_factor=K_FACTOR,
    initial=INITIAL,
    beta=BETA,
    rating_class=elo.CountedRating)

rng = np.arange(df.shape[0])

perm = np.random.permutation(rng)
for j in tqdm(perm):
    bot0 = df.iloc[j]['bot_0']
    bot1 = df.iloc[j]['bot_1']
    winner = bot1 if df.iloc[j]['winner_player'] else bot0
    loser = bot0 if df.iloc[j]['winner_player'] else bot1

    winner_elo, loser_elo = elo_calc.rate_1vs1(ratings[winner],
                                               ratings[loser],
                                               drawn=False)
    ratings[winner] = winner_elo
    ratings[loser] = loser_elo

rating_tuples = [(bot, rating) for bot, rating in ratings.items()]
pprint(sorted(rating_tuples, key=lambda x: x[1], reverse=True))

