# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ApartmentItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    description = scrapy.Field()
    rooms = scrapy.Field()
    m2 = scrapy.Field()
    kitchenm2 = scrapy.Field()
    restm2 = scrapy.Field()
    floor = scrapy.Field()
    totfloors = scrapy.Field()
    price = scrapy.Field()
    street = scrapy.Field()
    district = scrapy.Field()
    city = scrapy.Field()
    updated = scrapy.Field()
    lat = scrapy.Field()
    lon = scrapy.Field()
    
    wc = scrapy.Field() # watercloset
    walls = scrapy.Field()
    ceilings = scrapy.Field()
    rennovation = scrapy.Field()
    builtDate = scrapy.Field()
    postDate = scrapy.Field()

