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
import dateparser

def extract_date(value):
    value = sub('[\n]', '', value).strip()
    value = sub(u'Размещено', '', value).strip()
    print "POSTDATE",type(value),value.encode('utf-8')
    d = dateparser.parse(value)
    print "POSTDATE",d
    return d

def extract_price(value):
    #print 'extract_price',type(value),value.encode('utf-8')
    return ''.join(findall('\d+',value))
    
def extract_decimal(value):
    matches = findall(r"\d*\.\d+|\d+",value)
    if len(matches)>0:
        #print 'extract_decimal',type(value),value.encode('utf-8'),s
        return Decimal(matches[0])
    else:
        return None

def extract_rooms(value):
    if isinstance(value, basestring) and (u'студия' in value.lower() or u'гостиника' in value.lower()):
        return 0
    return value
    
def extract_int(value):
    #print 'extract_int type:%s value:"%s"' % (type(value),value.encode('utf-8'))
    if isinstance(value, basestring):
        s = findall(r"\d+",value)[0]
    elif isinstance(value, int):
        s = value
    else:
        raise 
    #print "value int: %d" % (int(s),)
    return int(s)
    
def remove_lines(value):
    return sub('[\n]', '', value)

class Apartment(Item):
    url = Field()
    description = Field()

    rooms = Field()
    floor = Field()
    totfloors = Field()

    m2 = Field()
    kitchenm2 = Field()
    restm2 = Field()

    price = Field()

    lat = Field(default=None)
    lon = Field(default=None)
    city = Field()
    street = Field()
    district = Field()
    
    wc = Field() # watercloset
    walls = Field()
    ceilings = Field()
    rennovation = Field()
    builtDate = Field()
    heating = Field()
    water = Field()
    balcony = Field()
    security = Field()

    postDate = Field()
    updated = Field()
        
class ApartmentLoader(ItemLoader):
    #default_input_processor = MapCompose(string.strip)
    default_output_processor = TakeFirst()

    description_in = MapCompose(unicode.strip, remove_lines)
    description_out = Join()

    floor_in = MapCompose(extract_int)
    totfloors_in = MapCompose(extract_int)
    rooms_in = MapCompose(extract_rooms, extract_int)
    
    m2_in = MapCompose(extract_decimal)
    restm2_in = MapCompose(extract_decimal)
    kitchenm2_in = MapCompose(extract_decimal)

    price_in = MapCompose(extract_price, extract_decimal)
        
    ceilings_in = MapCompose(extract_decimal)
    builtDate_in = MapCompose(extract_int)
    
    postDate_in = MapCompose(extract_date)
