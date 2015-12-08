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
from twisted.internet import threads

def get_guid(item):
    """Generates an unique identifier for a given item."""
    # hash based solely in the url field
    return hashlib.md5(item['url']).hexdigest()

class AvitoPipeline(object):
    def process_item(self, item, spider):
        return item

class PrintPipeline(object):
    def process_item(self, item, spider):
        #print " ==== PrintPipeline ===="
        spider.logger.debug("==== PrintPipeline ====")
        for name,val in item.items():
            #print name,':',val.encode('utf-8') if isinstance(val, unicode) else val
            #spider.logger.debug('%s:%s',name,val.encode('utf-8') if isinstance(val, unicode) else val)
            spider.logger.debug("%s%s:%s",name,type(val),val)
        spider.logger.debug("==== PrintPipeline ====")
        return item

class FilterPipeline(object):
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
        
        price = item.get('price',None)
        if price is None:
            raise DropItem("No price: %s" % item['url'])
        
        # run db query in the thread pool
        d = self.dbpool.runInteraction(self._detect_dup, item, spider)
        d.addErrback(self._handle_error, item, spider)
        # at the end return the item in case of success
        d.addCallback(lambda _: item)
        # return the deferred instead the item. This makes the engine to
        # process next item (according to CONCURRENT_ITEMS setting) after this
        # operation (deferred) has finished.
        return d

    def _detect_dup(self, conn, item, spider):        
        guid = get_guid(item)

        conn.execute("""SELECT EXISTS(
            SELECT 1 FROM realestate WHERE guid = %s
        )""", (guid, ))
        ret = conn.fetchone()[0]

        if ret:
            raise DropItem("Duplicate item found: %s" % guid)
        else:
            return item

    def _handle_error(self, failure, item, spider):
        """Handle occurred on db interaction."""
        # do nothing, just log  
         
        if not failure.check(DropItem):
            print 'DuplicatesPipeline fail',failure

        failure.raiseException()



class GeoPipeline(object):
    def __init__(self):
        #self.geolocator = geopy.geocoders.Nominatim()
        self.geolocator = geopy.geocoders.Yandex(timeout=5)
        
    def geocode(self, item, logger): 
        #fulladdr = ','.join((item['street'], item.get('district',''), item.get('city','')))
        fulladdr = ','.join((item['street'], item.get('city','')))
        location = self.geolocator.geocode(fulladdr)
        
        # call geopy to geocode item code 
        logger.debug('==== GeoPipeline ====')
        logger.debug('URL %s',item['url'])
        print "EXTRACTED ADDR", fulladdr.encode('utf-8')
        print "GEOCODED  ADDR", location.address.encode('utf-8')
        print (location.latitude, location.longitude)
        print repr(location.raw).decode("unicode-escape").encode('utf-8')
        print "PRECISION",location.raw[u'metaDataProperty'][u'GeocoderMetaData'][u'precision']
        logger.debug('==== GeoPipeline ====')
        if location.raw[u'metaDataProperty'][u'GeocoderMetaData'][u'precision'] in ['exact','number','near']:
            #item.lon = location.longitude
            #item.lat = location.latitude
            return (location.longitude, location.latitude)
        else:
            return None

    def process_item(self, item, spider): 
        def _onsuccess(geoinfo): 
            if geoinfo is not None:
                item['lon'], item['lat'] = geoinfo 
            return item 

        dfd = threads.deferToThread(self.geocode, item, spider.logger) 
        dfd.addCallback(_onsuccess) 
        return dfd

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
        #d.addBoth(lambda _: item)
        d.addCallback(lambda _: item)
        # return the deferred instead the item. This makes the engine to
        # process next item (according to CONCURRENT_ITEMS setting) after this
        # operation (deferred) has finished.
        return d

    def _do_upsert(self, conn, item, spider):
        print '_do_upsert'+repr(dict(item)).decode("unicode-escape").encode('utf-8') + "\n"
        
        """Perform an insert or update."""
        guid = get_guid(item)
        #now = datetime.utcnow().replace(microsecond=0).isoformat(' ')

        conn.execute("""SELECT EXISTS(
            SELECT 1 FROM realestate WHERE guid = %s
        )""", (guid, ))
        ret = conn.fetchone()[0]

        if ret:
            # conn.execute("""
                # UPDATE realestate
                # SET name=%s, description=%s, url=%s, updated=%s
                # WHERE guid=%s
            # """, (item['name'], item['description'], item['url'], now, guid))
            print("Item updated in db: %s" % (guid))
        else:
            conn.execute("""INSERT INTO realestate 
                (guid, url, description, rooms, floor, totfloors, m2, kitchenm2, restm2, price, city, district, street, updated, location, wc, walls, ceilings, rennovation, builtdate, heating, balcony, water, security, postDate)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, POINT(%s, %s), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, 
                (guid, 
                item['url'], 
                item['description'], 
                item['rooms'], 
                item['floor'], 
                item.get('totfloors',None), 
                item['m2'], 
                item.get('kitchenm2',None), 
                item.get('restm2',None),
                item['price'],
                item.get('city',None), 
                item.get('district',None), 
                item['street'], 
                item['updated'], 
                item.get('lon',None),
                item.get('lat',None),
                
                item.get('wc',None),
                item.get('walls',None),
                item.get('ceilings',None),
                item.get('rennovation',None),
                item.get('builtDate',None),
                item.get('heating',None),
                item.get('balcony',None),
                item.get('water',None),
                item.get('security',None),
                
                item.get('postDate',None),
                ))

            print("Item stored in db: %s" % (guid))

    def _handle_error(self, failure, item, spider):
        """Handle occurred on db interaction."""
        # do nothing, just log  
        # print "we got an exception: %s" % (failure.getTraceback(),)
        print 'MySQLStorePipeline fail',failure
        raise


