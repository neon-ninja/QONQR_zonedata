#!/bin/bash
filename=`date +%Y-%m-%d-%H%M%S`.sql.gz
sudo mysqldump qonqr | gzip > /mnt/mysqlbackups/$filename
find /mnt/mysqlbackups/ -mtime +10 -type f -delete # remove older than 10 days
