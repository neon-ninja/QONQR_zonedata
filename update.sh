#!/bin/bash
git pull
cd data
xargs -n 1 curl -ROfLs < ../links.txt
cd ..
python3 find_unique_zones.py
git -c user.name="QONQR-zonedata-bot" -c user.email="ubuntu@elevation.auckland-cer.cloud.edu.au" commit -am "auto update"
git push
curl https://raw.githubusercontent.com/neon-ninja/QONQR_zonedata/master/data/monthly_unique_zones.csv > /dev/null
