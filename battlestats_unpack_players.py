#!/usr/bin/env python3

import pandas as pd

def parse_row(row):
  bits = row.players.split(",")
  return pd.DataFrame({
    "Battle Report Number": row["Battle Report Number"],
    "Rank": bits[::5],
    "Player Name": bits[1::5],
    "Total Launches": bits[2::5],
    "Bots Killed": bits[3::5],
    "Bots Lost": bits[4::5]
  })

df = pd.read_csv("battlestats.csv")
player_df = pd.concat(df.apply(parse_row, axis=1).tolist())
player_df.to_csv("battlestats_players.csv", index=False)