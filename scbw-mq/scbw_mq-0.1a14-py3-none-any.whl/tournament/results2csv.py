import csv
import glob
import json

import pandas as pd
from tqdm import tqdm

result_dir = "/data/SSCAIT_2017/results_within_timelimit"


rows = {
    "game_name": [],
    "map": [],
    "bot_0": [],
    "bot_1": [],
    "read_overwrite": [],
    "game_time": [],
    "winner_player": []
}
for file in tqdm(glob.glob(f"{result_dir}/*.json")):
    with open(file, "r") as f:
        info = json.load(f)

    rows["game_name"].append(info["game_name"])
    rows["map"].append(info["map"])
    rows["bot_0"].append(info["bots"][0])
    rows["bot_1"].append(info["bots"][1])
    rows["read_overwrite"].append(info["read_overwrite"])
    rows["game_time"].append(info["game_time"])
    rows["winner_player"].append(info["winner_player"])

df = pd.DataFrame(rows).set_index("game_name")
df.to_csv("/data/SSCAIT_2017/results_within_timelimit.csv", quoting=csv.QUOTE_ALL)
