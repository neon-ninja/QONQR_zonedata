#!/usr/bin/env python3

import glob
import pandas as pd

df = pd.concat([pd.read_csv(f) for f in glob.glob('data/dailyzoneupdates-*.csv')], ignore_index = True)
df = df.sort_values('LastUpdateDateUtc', ascending=False).drop_duplicates(['ZoneId'])
df.to_csv("data/monthly_unique_zones.csv", index=False)