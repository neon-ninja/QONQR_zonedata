#!/usr/bin/env python3

import glob
import pandas as pd

df = pd.concat([pd.read_csv(f) for f in glob.glob('data/dailyzoneupdates-*.csv')], ignore_index = True)
df = df.sort_values('LastUpdateDateUtc', ascending=False).groupby("ZoneId").head(2)
grouped_df = df.groupby("ZoneId")
df["LegionDelta"] = grouped_df["LegionCount"].diff(-1)
df["SwarmDelta"] = grouped_df["SwarmCount"].diff(-1)
df["FacelessDelta"] = grouped_df["FacelessCount"].diff(-1)
df["TotalCount"] = df["LegionCount"] + df["SwarmCount"] + df["FacelessCount"]
df["TotalDelta"] = df["LegionDelta"].abs() + df["SwarmDelta"].abs() + df["FacelessDelta"].abs()
df = df.drop_duplicates(['ZoneId'])
df.to_csv("data/monthly_unique_zones.csv", index=False)