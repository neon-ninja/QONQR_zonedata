#!/usr/bin/env python3

from bs4 import BeautifulSoup
import pandas as pd
import requests
import sys
import mysql.connector
import config

db = mysql.connector.connect(
    host="localhost",
    user=config.user,
    password=config.password,
    database="qonqr",
    autocommit=True
)
cur = db.cursor(dictionary=True)

def parse_html(BRN, html):
    soup = BeautifulSoup(html, features="lxml")
    h1 = soup.find("h1")
    row = {
        "Battle Report Number": BRN
    }
    bits = h1.get_text("\n", strip=True).split("\n")
    if bits[0] == "/":
        raise Exception("Blank title")
    row["Zone Name"] = bits[0]
    countrybits = bits[1].split(" / ")
    row["Region"] = countrybits[0]
    row["Country"] = countrybits[1]
    row["Zone ID"] = bits[2].strip("#")
    row["Date"] = pd.to_datetime(soup.find("strong").string)
    swarmStart, legionStart, facelessStart, swarmEnd, legionEnd, facelessEnd = [int(e.get_text(strip=True)) for e in soup.find_all("div", class_="progress")]
    row["Swarm Starting Bots"] = swarmStart
    row["Legion Starting Bots"] = legionStart
    row["Faceless Starting Bots"] = facelessStart
    row["Swarm Ending Bots"] = swarmEnd
    row["Legion Ending Bots"] = legionEnd
    row["Faceless Ending Bots"] = facelessEnd
    for div in soup.find_all("div", class_="col-md-5"):
        bits = div.get_text("\n", strip=True).split("\n")
        stat_name = bits[0].strip(":")
        row[stat_name] = int(bits[1].replace(" ", ""))
        table = div.find_next_sibling("div", class_="col-md-7")
        for td in table.find_all("td"):
            faction = td.attrs['class'][0]
            row[f"{faction} {stat_name}"] = int(td.string.replace(" ", ""))
    playerTable = soup.select_one("div.col-sm-6 > div.table-responsive > table > tbody")
    row["players"] = playerTable.get_text(",", strip=True).replace(" ", "")
    if not row["players"]:
        raise Exception("No players")
    return row

df = pd.read_csv("battlestats.csv")
BRN = df["Battle Report Number"].max()
assert BRN >= 117536

# Get the current max BRN (contained in the last link of the MAZ page)
html = requests.get("https://portal.qonqr.com/Home/MostActiveZones").text
soup = BeautifulSoup(html, features="lxml")
links = soup.find_all("a")
last_link = links[-1]["href"]
CURRENT_BRN = int(last_link.split("/")[-1])
print(f"Last BRN is {BRN}, current BRN is {CURRENT_BRN}")
if BRN == CURRENT_BRN:
    print("Up to date, exiting")
    sys.exit(1)

new_rows = []

while BRN <= CURRENT_BRN:
    try:
        BRN += 1
        print(BRN)
        r = requests.get(f"https://portal.qonqr.com/Home/BattleStatistics/{BRN}")
        new_row = parse_html(BRN, r.text)
        keys = ",".join([f"`{k}`" for k in new_row.keys()])
        values = ",".join([f'"{v}"' for v in new_row.values()])
        sql = f"REPLACE INTO battlestats ({keys}) VALUES ({values})"
        print(sql)
        cur.execute(sql)
        new_rows.append(new_row)
    except Exception as e:
        print(BRN, e)

new_rows = pd.DataFrame(new_rows)
df = pd.concat([df, new_rows])
print(df)
df = df[~df.players.isna()]
df.Date = pd.to_datetime(df.Date)
df.to_csv("battlestats.csv", index=False, date_format='%Y-%m-%d')
