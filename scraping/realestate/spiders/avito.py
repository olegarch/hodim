#!/usr/bin/env python
# -*- coding: utf8 -*-

import scrapy
from realestate.items import Apartment, ApartmentLoader
import re
from datetime import datetime
from decimal import *


class AvitoSpider(scrapy.Spider):
    name = "avito"
    allowed_domains = ["avito.ru"]
    start_urls = [
        "https://www.avito.ru/rostov-na-donu/kvartiry/prodam",
    ]

    def parse(self, response):
            
        for href in response.xpath('//h3[@class="title"]/a/@href').extract():
            url = response.urljoin(href)
            yield scrapy.Request(url, callback=self.parse_item_page)
            
        next_page_href = response.xpath(u"//a[@class='pagination__page' and contains(text(),'Следующая') ]/@href").extract()[0]
        next_url = response.urljoin(next_page_href)
        yield scrapy.Request(next_url, callback=self.parse)
        
    def parse_item_page(self, response):
        filename = 'avito' + response.url[-10:] + '.html'
        #self.logger.info('filename %s',filename)
        with open(filename, 'wb') as f:
            f.write(response.body)
            
        l = ApartmentLoader(Apartment(), response)
        l.add_value('url', response.url)
        
        # 1-к квартира, 42 м², 12/18 эт.
        # Студия, 28 м², 2/5 эт.
        # > 9-к квартира, 336 м², 23/23 эт
        #title = response.xpath('//h1[@itemprop="name" and @class="h1"]/text()').extract()
        #assert 1==len(title)        
        #m = re.search(u"(?:(\d+)-к квартира|(Студия)),\s+(\d+)\s+м²,\s+(\d+)/(\d+)\s+эт", title[0], flags=re.UNICODE)
        #print title[0].encode('utf-8')
        #print m.groups()
        
        #l.add_xpath('description', '//h1[@itemprop="name" and @class="h1"]/text()', re=u'(?:(\d+)-к квартира|(Студия))')
        l.add_xpath('rooms', '//h1[@itemprop="name" and @class="h1"]/text()', re=u'(Студия)')
        l.add_xpath('rooms', '//h1[@itemprop="name" and @class="h1"]/text()', re=u'(?:(\d+)-к квартира)')
        l.add_xpath('m2', '//h1[@itemprop="name" and @class="h1"]/text()', re=u',\s+(\d+)\s+м²,')
        l.add_xpath('floor', '//h1[@itemprop="name" and @class="h1"]/text()', re=u'\s+(\d+)/\d+\s+эт')
        l.add_xpath('totfloors', '//h1[@itemprop="name" and @class="h1"]/text()', re=u'\s+\d+/(\d+)\s+эт')
        l.add_xpath('price', '//span[@itemprop="price"]/text()')
        
        l.add_xpath('city', '//meta[@itemprop="addressLocality"]/@content')
        l.add_xpath('district', '//span[@itemprop="streetAddress"]/text()')
        l.add_xpath('street', '//span[@itemprop="streetAddress"]/text()')
        
        description = ' '.join(response.xpath('//div[@class="description description-text"]/descendant::*/text()').extract())
        print description.encode('utf-8')
        
        l.add_xpath('description', '//div[@class="description description-text"]/descendant::*/text()')
        
        l.add_value('updated', datetime.utcnow().isoformat())
        # #item > div.g_123 > div.l-content.clearfix > div.clearfix > div.g_92 > div.item-subtitle
        l.add_xpath('postDate', '//div[@class="item-subtitle"]/text()')
        yield l.load_item()
        
        return
        
        m = re.search(u"(?:(\d+)-к квартира|(Студия)),\s+(\d+)\s+м²,\s+(\d+)/(\d+)\s+эт", title[0], flags=re.UNICODE)
        
        if m is not None:
            if m.group(1) is not None:
                rooms = int(m.group(1))
            else:
                rooms = 0
            m2 = Decimal(m.group(3))
            floor = int(m.group(4))
            totfloors = int(m.group(5))
        
        #print 'ROOMS:',rooms
        #print 'SPACE:',m2
        #print 'FLOOR:',floor,'/',totfloors
        
        price_text = response.xpath('//span[@itemprop="price"]/text()').extract()
        
        try:
            price = int(''.join(re.findall('\d+',price_text[0])))
            #print 'PRICE:',price
        except ValueError as err:
            print '"%s" is not valide price: %s' % (price_text[0].encode('utf-8'), err)
            price = None
        
        city = ' '.join(response.xpath('//meta[@itemprop="addressLocality"]/@content').extract())
        #print 'CITY:',city.encode('utf-8')
        district = ' '.join(response.xpath('//span[@itemprop="streetAddress"]/parent::span/text()').extract())
        #print 'DISTRICT:',district.encode('utf-8')
        street = ' '.join(response.xpath('//span[@itemprop="streetAddress"]/text()').extract())
        #print 'STREET:',street.encode('utf-8')
        description = ' '.join(response.xpath('//div[@class="description description-text"]/descendant::*/text()').extract())
        #print 'DESC:',description.encode('utf-8')
        id = response.xpath('//div[@class="item-sku"]/span[@id="item_id"]/text()').extract()
        assert 1==len(id)
        #print 'ID:','avito'+id[0].encode('utf-8')
        #print '------------------------------------------------------'
        
        item = Apartment()
        item['url'] = response.url
        item['street'] = street
        item['district'] = district
        item['city'] = city
        item['description'] = description
        item['floor'] = floor
        item['totfloors'] = totfloors
        item['m2'] = m2
        item['rooms'] = rooms
        item['price'] = price
        #item['id'] = 'avito'+id[0]
        item['updated'] = datetime.utcnow().isoformat()

        yield item