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

cur = db.cursor()

for f in files:
    df = pd.read_csv(f, dtype=str)
    df = df.fillna("NULL")
    for i, row in tqdm(df.iterrows(), total=df.shape[0]):
        values = ",".join([f'"{v}"' if v != "NULL" else v for v in row.values])
        sql = f"""REPLACE INTO zones ({','.join(row.index)}) VALUES ({values})"""
        cur.execute(sql)
