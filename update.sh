#!/bin/bash
git pull
cd data
xargs -n 1 curl -ROLs < ../links.txt
git commit -am "auto update"
git push
