#!/bin/bash

cd /home/ubuntu/hodim/scraping
PATH=$PATH:/usr/local/bin
export PATH
now=$(date +"%m_%d_%Y_%H_%M_%S")
scrapy crawl avito -s DEPTH_LIMIT=20000 -o avito.jl 2>&1 | tee avito_$now.log
