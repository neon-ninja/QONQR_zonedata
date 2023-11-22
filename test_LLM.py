#!/usr/bin/env python3.10

import pandas as pd
from pandasai import SmartDataframe, SmartDatalake
from langchain.chat_models import ChatOpenAI
import logging
logging.basicConfig()
logging.getLogger("pandasai").setLevel(logging.DEBUG)

df = SmartDataframe("battlestats.csv", config={
    "name": "battles",
    "description": "MAZ battles",
    "llm": ChatOpenAI(),
    "enable_cache": False,
    "custom_whitelisted_dependencies": ["PIL"]
}).drop(columns=["players"])
player_df = SmartDataframe("battlestats_players.csv", config={
    "name": "players",
    "description": "players who fought in the MAZ battles",
    "llm": ChatOpenAI(),
    "enable_cache": False,
    "custom_whitelisted_dependencies": ["PIL"],
})
player_details_df = SmartDataframe("player_details.csv", config={
    "name": "player details",
    "description": "Details about players",
    "llm": ChatOpenAI(),
    "enable_cache": False,
    "custom_whitelisted_dependencies": ["PIL"],
})
df = SmartDatalake([df, player_df, player_details_df], config={"llm": ChatOpenAI(), "enable_cache": False, "max_retries": 10})
print(df.chat('How many active players are there in each faction?'))
print(df.last_result)
print(df.last_code_executed)