# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import geopy
import json
from scrapy.exceptions import DropItem
from twisted.enterprise import adbapi
import hashlib
#from datetime import datetime

class AvitoPipeline(object):
    def process_item(self, item, spider):
        return item
        
class GeoPipeline(object):
    def __init__(self):
        #self.geolocator = geopy.geocoders.Nominatim()
        self.geolocator = geopy.geocoders.Yandex(timeout=2)

    def process_item(self, item, spider):
        fulladdr = ','.join((item['street'], item['district'], item['city']))
        location = self.geolocator.geocode(fulladdr)
        
        try:
            location = self.geolocator.geocode(fulladdr)
        except geopy.exc.GeocoderTimedOut as e:
            print("Error: geocode failed with message '%s'"%(e.message))
            location = self.geolocator.geocode(fulladdr,timeout=10)
    
        print '======================================================'
        print "EXTRACTED ADDR", fulladdr.encode('utf-8')
        print "GEOCODED  ADDR", location.address.encode('utf-8')
        print (location.latitude, location.longitude)
        print repr(location.raw).decode("unicode-escape").encode('utf-8')
        print "PECISION",location.raw[u'metaDataProperty'][u'GeocoderMetaData'][u'precision']
        print '======================================================'
        if location.raw[u'metaDataProperty'][u'GeocoderMetaData'][u'precision'] in ['exact','number','near']:
            item['lon'] = location.longitude
            item['lat'] = location.latitude
        return item

class JsonWriterPipeline(object):
    def __init__(self):
        self.file = open('avito1.jl', 'wb')

    def process_item(self, item, spider):
        line = repr(dict(item)).decode("unicode-escape").encode('utf-8') + "\n"
        self.file.write(line + "\n")
        return item
        
class MySQLStorePipeline(object):
    """A pipeline to store the item in a MySQL database.
    This implementation uses Twisted's asynchronous database API.
    """

    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbargs = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            charset='utf8',
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbargs)
        return cls(dbpool)

    def process_item(self, item, spider):
        # run db query in the thread pool
        d = self.dbpool.runInteraction(self._do_upsert, item, spider)
        d.addErrback(self._handle_error, item, spider)
        # at the end return the item in case of success or failure
        d.addBoth(lambda _: item)
        # return the deferred instead the item. This makes the engine to
        # process next item (according to CONCURRENT_ITEMS setting) after this
        # operation (deferred) has finished.
        return d

    def _do_upsert(self, conn, item, spider):
        """Perform an insert or update."""
        guid = self._get_guid(item)
        #now = datetime.utcnow().replace(microsecond=0).isoformat(' ')

        conn.execute("""SELECT EXISTS(
            SELECT 1 FROM realestate WHERE guid = %s
        )""", (guid, ))
        ret = conn.fetchone()[0]

        if ret:
            pass
            # conn.execute("""
                # UPDATE realestate
                # SET name=%s, description=%s, url=%s, updated=%s
                # WHERE guid=%s
            # """, (item['name'], item['description'], item['url'], now, guid))
            print("Item updated in db: %s %r" % (guid, item))
        else:
            if 'lat' in item:
                loc = "POINT(%s,%s)" % (item['lon'],item['lat'])
                print "#### LOC",loc
                conn.execute("""
                    INSERT INTO realestate (guid, url, id, title, description, rooms, floor, totfloors, m2, price,  city, district, street, updated, location)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, POINT(%s,%s))
                """, (guid, item['url'], item['id'], item['title'], item['description'], item['rooms'], 
                      item['floor'], item['totfloors'], item['m2'], item['price'], 
                      item['city'], item['district'], item['street'], item['updated'],
                      item['lon'],item['lat']))
            else:
                loc = 'NULL'
                conn.execute("""
                    INSERT INTO realestate (guid, url, id, title, description, rooms, floor, totfloors, m2, price,  city, district, street, updated)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (guid, item['url'], item['id'], item['title'], item['description'], item['rooms'], 
                      item['floor'], item['totfloors'], item['m2'], item['price'], 
                      item['city'], item['district'], item['street'], item['updated']
                      ))
                
            # conn.execute("""
                # INSERT INTO realestate (guid, url, id, title, description, rooms, floor, totfloors, m2, price,  city, district, street, updated, location)
                # VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            # """, (guid, item['url'], item['id'], item['title'], item['description'], item['rooms'], 
                  # item['floor'], item['totfloors'], item['m2'], item['price'], 
                  # item['city'], item['district'], item['street'], item['updated'],
                  # loc))
 
            print("Item stored in db: %s %r" % (guid, item))

    def _handle_error(self, failure, item, spider):
        """Handle occurred on db interaction."""
        # do nothing, just log
        print(failure)

    def _get_guid(self, item):
        """Generates an unique identifier for a given item."""
        # hash based solely in the url field
        return hashlib.md5(item['url']).hexdigest()
