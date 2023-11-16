#!/usr/bin/env python3.10

import pandas as pd
from pandasai import SmartDataframe, SmartDatalake
from langchain.chat_models import ChatOpenAI
import logging
logging.basicConfig()
logging.getLogger("pandasai").setLevel(logging.DEBUG)

df = SmartDataframe("battlestats.csv", config={
    "name": "battles",
    "llm": ChatOpenAI(),
    "enable_cache": False,
    "custom_whitelisted_dependencies": ["PIL"]
}).drop(columns=["players"])
player_df = SmartDataframe("battlestats_players.csv", config={
    "name": "players",
    "llm": ChatOpenAI(),
    "enable_cache": False,
    "custom_whitelisted_dependencies": ["PIL"]
})
df = SmartDatalake([df, player_df], config={"llm": ChatOpenAI(), "enable_cache": False})
print(df.chat('Group by player name, sum their Total Launches in battles where the country is not Atlantis, sort descending, then print the top 10 as a table'))
print(df.last_result)