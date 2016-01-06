#!/bin/bash

cd /home/ubuntu/hodim/scraping
now=$(date +"%m_%d_%Y_%H_%M_%S")
scrapy crawl avito -o avito.jl 2>&1 | tee avito_$now.log
