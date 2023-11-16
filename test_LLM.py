#!/usr/bin/env python3.10

import pandas as pd
from pandasai import SmartDataframe
from langchain.chat_models import ChatOpenAI
import logging
logging.basicConfig()
logging.getLogger("pandasai").setLevel(logging.DEBUG)

df = SmartDataframe("battlestats.csv", config={"llm": ChatOpenAI()})
print(df.chat('Print out the top 10 Zones'))
print(df.last_result)
print(df.chat('Plot the top 10 Zones'))
print(df.last_result)