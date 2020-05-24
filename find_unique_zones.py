#!/usr/bin/env python3

import glob
import pandas as pd

df = pd.concat([pd.read_csv(f) for f in glob.glob('data/dailyzoneupdates-*.csv')], ignore_index = True)
df = pd.concat([df, pd.read_csv("data/monthly_unique_zones.csv")], ignore_index = True)
df = df.drop_duplicates(["ZoneId","LastUpdateDateUtc"])
print("Data loaded")
df = df.sort_values('LastUpdateDateUtc', ascending=False).groupby("ZoneId").head(2)
print("Sorted")
grouped_df = df.groupby("ZoneId")
print("Grouped")
df["LegionDelta"] = grouped_df["LegionCount"].diff(-1)
print("LegionDelta")
df["SwarmDelta"] = grouped_df["SwarmCount"].diff(-1)
print("SwarmDelta")
df["FacelessDelta"] = grouped_df["FacelessCount"].diff(-1)
print("FacelessDelta")
df["TotalCount"] = df["LegionCount"] + df["SwarmCount"] + df["FacelessCount"]
df["TotalDelta"] = df["LegionDelta"].abs() + df["SwarmDelta"].abs() + df["FacelessDelta"].abs()
df = df.drop_duplicates(['ZoneId'])
df = df.drop(columns=["UtmGrid", "GridRef"])
df = df.sort_values(by=list(df.columns), ascending=False)
print("Calculated")
df.to_csv("data/monthly_unique_zones.csv", index=False, float_format='%g')
df[df.CountryId == 180].to_csv("data/poland.csv", index=False, float_format='%g')
print("Saved")
