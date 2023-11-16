#!/usr/bin/env python3
import pandas as pd
pd.set_option("display.max_columns", None)

df = pd.read_csv("battlestats.csv")
print(df.loc[df.Country!="Atlantis", ["Zone Name", "Region", "Country"]].value_counts().head(100))
