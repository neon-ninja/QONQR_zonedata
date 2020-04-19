#!/bin/bash
git pull
cd data
xargs -n 1 curl -ROLs < ../links.txt
python find_unique_zones.py
git commit -am "auto update"
git push
