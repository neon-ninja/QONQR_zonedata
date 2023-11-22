#!/usr/bin/env python3

import os
import pandas as pd
from dotenv import load_dotenv
load_dotenv()
from pprint import pprint
from tqdm.auto import tqdm

from requests_html import HTMLSession
s = HTMLSession()

df = pd.read_csv("battlestats_players.csv")
players = df["Player Name"].unique()

token = s.get("https://portal.qonqr.com/Home/Login").html.find("input[name='__RequestVerificationToken']", first=True).attrs['value']
login_result = s.post("https://portal.qonqr.com/Home/Login", data={"__RequestVerificationToken": token, "Username": os.getenv("QONQR_USERNAME"), "Password": os.getenv("QONQR_PASSWORD")})

results = []

for i, player in enumerate(tqdm(players)):
  html = s.get(f"https://portal.qonqr.com/Player/Details/{player}").html
  player_elems = html.find("div.inset>div.row>div.col-xs-7",first=True)
  if not player_elems:
    print(f"Can't player_elems for {player}")
    continue
  name, level, faction = [h3.text.strip() for h3 in player_elems.find("h3")]
  level = int(level.replace("Level ", ""))
  active = player_elems.find("div")[-1].text.strip().split("\n")[0]
  profile_pic = html.find("img.img-responsive", first=True).attrs["src"]
  start_date = str(pd.to_datetime(html.find("div.media.blue small", first=True).text).date())
  player = {
      "name": name,
      "level": level,
      "faction": faction,
      "active": active,
      "start_date": start_date,
      "profile_pic": profile_pic
  }
  results.append(player)
  if i % 100 == 0:
    pd.DataFrame(results).to_csv("player_details.csv", index=False)
pd.DataFrame(results).to_csv("player_details.csv", index=False)