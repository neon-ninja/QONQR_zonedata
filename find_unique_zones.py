#!/usr/bin/env python3

import glob
import pandas as pd
from datetime import datetime, timedelta

INT_COLS = ["LegionCount", "SwarmCount", "FacelessCount", "LegionDelta", "SwarmDelta", "FacelessDelta", "TotalCount", "TotalDelta"]

df = pd.concat([pd.read_csv("data/monthly_unique_zones.csv")] + [pd.read_csv(f) for f in glob.glob('data/dailyzoneupdates-*.csv')], ignore_index = True)
df = df.drop_duplicates(["ZoneId","LastUpdateDateUtc"])
df.LastUpdateDateUtc = pd.to_datetime(df.LastUpdateDateUtc).dt.floor("s")
df.DateCapturedUtc = pd.to_datetime(df.DateCapturedUtc).dt.floor("s")
mindate = str(datetime.utcnow() - timedelta(days=31))
df = df[(df.LastUpdateDateUtc > mindate) | ~df.TotalCount.isna()] # filter out day 31
print("Data loaded")
df = df.sort_values('LastUpdateDateUtc', ascending=False).groupby("ZoneId").head(2)
print("Sorted")
grouped_df = df.groupby("ZoneId")
print("Grouped")
agg = {}
agg["LegionDelta"] = grouped_df["LegionCount"].diff(-1)
print("LegionDelta")
agg["SwarmDelta"] = grouped_df["SwarmCount"].diff(-1)
print("SwarmDelta")
agg["FacelessDelta"] = grouped_df["FacelessCount"].diff(-1)
print("FacelessDelta")
df.update(agg)
df["TotalCount"] = df["LegionCount"] + df["SwarmCount"] + df["FacelessCount"]
df["TotalDelta"] = df["LegionDelta"].abs() + df["SwarmDelta"].abs() + df["FacelessDelta"].abs()
df = df.drop_duplicates(['ZoneId'])
df = df.drop(columns=["UtmGrid", "GridRef"])
df = df.sort_values(by=list(df.columns), ascending=False)
df[INT_COLS] = df[INT_COLS].astype("Int64")
print("Calculated")
df.to_csv("data/monthly_unique_zones.csv", index=False, float_format='%.10g')
df[df.CountryId == 180].to_csv("data/poland.csv", index=False, float_format='%.10g')
print("Saved")
