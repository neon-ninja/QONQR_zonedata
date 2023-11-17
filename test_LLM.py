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
df = SmartDatalake([df, player_df], config={"llm": ChatOpenAI(), "enable_cache": False, "max_retries": 10})
print(df.chat('Find all players who fought in battles where the Region is Ohio. Group by Player Name, and sum their Total Launches in those battles. Sort by the summed Total Launches descending, and output the top 10 as a table'))
print(df.last_result)
print(df.last_code_executed)