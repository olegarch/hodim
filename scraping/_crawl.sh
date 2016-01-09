#!/bin/bash

cd /home/ubuntu/hodim/scraping
PATH=$PATH:/usr/local/bin
export PATH
now=$(date +"%m_%d_%Y_%H_%M_%S")
scrapy crawl $1 -s DEPTH_LIMIT=20000 -o $1.jl 2>&1 | tee $1_$now.log
