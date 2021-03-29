#!/usr/bin/env python3

# DB seeded with
# LOAD DATA INFILE "AllZones.csv" INTO TABLE zones FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' LINES TERMINATED BY '\r\n' IGNORE 1 LINES (ZoneId,Description,RegionId,CountryId,UtmGrid,GridRef,ZoneControlState,@DateCapturedUtc,LegionCount,SwarmCount,FacelessCount,@LastUpdateDateUtc,Latitude,Longitude) SET DateCapturedUtc = IF(@DateCapturedUtc = '', NULL, @DateCapturedUtc), LastUpdateDateUtc = IF(@LastUpdateDateUtc = '', NULL, @LastUpdateDateUtc);

import mysql.connector
import config
import pandas as pd
import sys
from tqdm.auto import tqdm

db = mysql.connector.connect(
    host="localhost",
    user=config.user,
    password=config.password,
    database="qonqr",
    autocommit=True
)

if len(sys.argv) > 1:
    files = sys.argv[1:]

cur = db.cursor(dictionary=True)

for f in files:
    print(f"Loading {f}")
    df = pd.read_csv(f)
    df.DateCapturedUtc = pd.to_datetime(df.DateCapturedUtc).dt.floor("s")
    df.LastUpdateDateUtc = pd.to_datetime(df.LastUpdateDateUtc).dt.floor("s")
    print("Loaded. Fetching existing data...")
    cur.execute(f"SELECT * FROM zones WHERE ZoneID IN ({','.join(df.ZoneId.astype(str))})")
    existing_data = cur.fetchall()
    print(f"{len(existing_data)} existing rows fetched")
    updates = 0
    for e in tqdm(existing_data):
        match = df[df.ZoneId == e["ZoneId"]].iloc[0].to_dict()
        if not e["LastUpdateDateUtc"] or match["LastUpdateDateUtc"] > e["LastUpdateDateUtc"]:
            match["TotalCount"] = match["LegionCount"] + match["SwarmCount"] + match["FacelessCount"]
            match["LegionDelta"] = match["LegionCount"] - e["LegionCount"]
            match["SwarmDelta"] = match["SwarmCount"] - e["SwarmCount"]
            match["FacelessDelta"] = match["FacelessCount"] - e["FacelessCount"]
            match["TotalDelta"] = abs(match["LegionDelta"]) + abs(match["SwarmDelta"]) + abs(match["FacelessDelta"])
            for k, v in match.items():
                if pd.isnull(v):
                    match[k] = "NULL"
                else:
                    match[k] = f'"{v}"'
            sql = f"""REPLACE INTO zones ({','.join(match.keys())}) VALUES ({','.join(match.values())})"""
            updates += 1
            cur.execute(sql)
    print(f"Did {updates} updates")
