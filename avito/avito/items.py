# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose, Join
from decimal import Decimal
from re import findall, sub

def extract_price(value):
    #print 'extract_price',type(value),value.encode('utf-8')
    return ''.join(findall('\d+',value))
    
def extract_decimal(value):
    s = findall(r"\d*\.\d+|\d+",value)[0]
    #print 'extract_decimal',type(value),value.encode('utf-8'),s
    return Decimal(s)

def extract_int(value):
    s = findall(r"\d+",value)[0]
    #print 'extract_int',type(value),value.encode('utf-8'),s
    return int(s)
    
def remove_lines(value):
    return sub('[\n]', '', value)

class Apartment(Item):
    id = Field()
    title = Field()
    url = Field()
    description = Field()
    rooms = Field()
    m2 = Field()
    kitchenm2 = Field()
    restm2 = Field()
    floor = Field()
    totfloors = Field()
    price = Field()
    street = Field()
    district = Field()
    city = Field()
    updated = Field()
    lat = Field(default=None)
    lon = Field(default=None)
    
    wc = Field() # watercloset
    walls = Field()
    ceilings = Field()
    rennovation = Field()
    builtDate = Field()
    postDate = Field()
    heating = Field()
    water = Field()
    balcony = Field()
        
class ApartmentLoader(ItemLoader):
    #default_input_processor = MapCompose(string.strip)
    default_output_processor = TakeFirst()
    
    price_in = MapCompose(extract_price, extract_decimal)
    m2_in = MapCompose(extract_decimal)
    restm2_in = MapCompose(extract_decimal)
    kitchenm2_in = MapCompose(extract_decimal)
    
    floor_in = MapCompose(extract_int)
    totfloors_in = MapCompose(extract_int)
    rooms_in = MapCompose(extract_int)
    
    description_in = MapCompose(unicode.strip, remove_lines)
    description_out = Join()
    
