#!/usr/bin/env python3

import os
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

from requests_html import HTMLSession
s = HTMLSession()

df = pd.read_csv("exchange_rates.csv")
today = str(pd.Timestamp.utcnow().date())
if df.date.max() == today:
  print("Already updated today")
  exit(1)

token = s.get("https://portal.qonqr.com/Home/Login").html.find("input[name='__RequestVerificationToken']", first=True).attrs['value']
login_result = s.post("https://portal.qonqr.com/Home/Login", data={"__RequestVerificationToken": token, "Username": os.getenv("QONQR_USERNAME"), "Password": os.getenv("QONQR_PASSWORD")})
# <input data-val="true" data-val-required="The CubeToQred field is required." id="CubeToQred" name="CubeToQred" type="hidden" value="3500" />
CubeToQred = s.get("https://portal.qonqr.com/Depot/Exchange").html.find("input[name='CubeToQred']", first=True).attrs['value']
row = pd.DataFrame({"date": today, "CubeToQred": CubeToQred}, index=[0])
df = pd.concat([df, row])
print(df)
df.to_csv("exchange_rates.csv", index=False)