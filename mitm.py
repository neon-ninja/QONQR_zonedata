#!/usr/bin/env python3

## Usage: mitmdump -s mitm.py

from mitmproxy import http
import json
import csv

seen_ids = []
csvwriter = None

urllog = open(file="urls.txt", mode="w", buffering=1)

def response(flow: http.HTTPFlow):
    global seen_ids, csvwriter
    if flow.request.pretty_url.startswith("https://api.qonqr.com/v2/Zones/Pins"):
        data = json.loads(flow.response.content)
        has_new_data = False
        for zone in data["zones"]:
            if not csvwriter:
                print(",".join(zone.keys()))
                csvwriter = csv.DictWriter(open(file="zones.csv", mode="w", buffering=1, newline=''), fieldnames=zone.keys())
                csvwriter.writeheader()
            print(",".join(str(x or "") for x in zone.values()))
            if zone["zoneId"] not in seen_ids:
                has_new_data = True
                seen_ids.append(zone["zoneId"])
                csvwriter.writerow(zone)
        if has_new_data:
            print(flow.request.pretty_url, file=urllog)
