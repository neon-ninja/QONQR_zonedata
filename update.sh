#!/bin/bash
git pull
cd data
xargs -n 1 curl -ROLsz < ../links.txt
git commit -am "auto update"
git push
