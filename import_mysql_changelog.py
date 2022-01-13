#!/usr/bin/env python3

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

cur.execute(f"SELECT MAX(LastUpdateDateUtc) as latest FROM changelog")
latest = cur.fetchone()["latest"]
print(f"Latest change recorded {latest}")

keys = "ZoneId, ZoneControlState, DateCapturedUtc, LegionCount, SwarmCount, FacelessCount, LastUpdateDateUtc".split(", ")

for f in files:
    print(f"Loading {f}")
    df = pd.read_csv(f)
    df = df[~pd.isnull(df.LastUpdateDateUtc)]
    df.DateCapturedUtc = pd.to_datetime(df.DateCapturedUtc).dt.floor("s")
    df.LastUpdateDateUtc = pd.to_datetime(df.LastUpdateDateUtc).dt.floor("s")
    df = df[df.LastUpdateDateUtc > latest]
    print(f"{len(df)} rows to apply")
    updates = 0
    for i, row in tqdm(df.iterrows(), total=len(df)):
        row = {k: row[k] for k in keys}
        for k, v in row.items():
            if pd.isnull(v):
                row[k] = "NULL"
            else:
                row[k] = f'"{v}"'
        sql = f"""REPLACE INTO changelog ({','.join(row.keys())}) VALUES ({','.join(row.values())})"""
        updates += 1
        cur.execute(sql)
    print(f"Did {updates} updates")
    