#!/usr/bin/env python3

from bs4 import BeautifulSoup
import os
import csv
from tqdm.auto import tqdm

writer = None

files = sorted([int(f.replace(".html", "")) for f in os.listdir("battlestats_html")])

for i in tqdm(files):
    with open(f"battlestats_html/{i}.html") as f:
        soup = BeautifulSoup(f.read(), features="lxml")
    h1 = soup.find("h1")
    row = {
        "Battle Report Number": i
    }
    bits = h1.get_text("\n", strip=True).split("\n")
    if bits[0] == "/":
        continue
    row["Zone Name"] = bits[0]
    row["Country"] = bits[1]
    row["Zone ID"] = bits[2]
    row["Date"] = soup.find("strong").string
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

    if not writer:
        writer = csv.DictWriter(open('battlestats.csv', 'w', newline=''), fieldnames=row.keys())
        writer.writeheader()
    writer.writerow(row)