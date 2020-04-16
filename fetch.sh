#!/bin/bash
cd data
xargs -n 1 curl -ROLs < ../links.txt