#!/bin/bash
git pull
cd data
xargs -n 1 curl -ROfLs < ../links.txt
cd ..
python3 find_unique_zones.py
git commit -am "auto update"
git push
