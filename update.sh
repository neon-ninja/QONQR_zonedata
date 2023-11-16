#!/bin/bash
git pull
cd data
xargs -n 1 curl -ROfLs < ../links.txt
cd ..
python3 import_mysql.py data/dailyzoneupdates-*
python3 import_mysql_changelog.py data/dailyzoneupdates-*
python3 update_battlestats.py
python3 battlestats_unpack_players.py
python3 get_exchange_rate.py
#python3 find_unique_zones.py
sudo mysql -Be "SELECT ZoneId,Description,RegionId,CountryId,ZoneControlState,DateCapturedUtc,LegionCount,SwarmCount,FacelessCount,LastUpdateDateUtc,Latitude,Longitude,LegionDelta,SwarmDelta,FacelessDelta,TotalCount,TotalDelta FROM qonqr.zones WHERE DATEDIFF(CURDATE(), LastUpdateDateUtc) < 30 ORDER BY TotalCount DESC" > data/monthly_unique_zones.csv
git add data *.csv
git commit -m "auto update" --author="QONQR-zonedata-bot <ubuntu@elevation.auckland-cer.cloud.edu.au>"
git push
curl https://raw.githubusercontent.com/neon-ninja/QONQR_zonedata/master/data/monthly_unique_zones.csv > /dev/null
