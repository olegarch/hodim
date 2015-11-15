#!/usr/bin/env python
# -*- coding: utf8 -*-

import scrapy
from avito.items import ApartmentItem
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
            print href
            print url
            yield scrapy.Request(url, callback=self.parse_item_page)
            
        #next_page_href = response.xpath('//a[@class="pagination__page" and contains(text(),"Следующая")]/@href').extract()
        #for l in response.xpath(u"//a[@class='pagination__page']/text()").extract():
        #    print "PAGE:",l.encode('utf-8')

        next_page_href = response.xpath(u"//a[@class='pagination__page' and contains(text(),'Следующая') ]/@href").extract()[0]
        next_url = response.urljoin(next_page_href)
        print 'NEXT:',next_url
        yield scrapy.Request(next_url, callback=self.parse)
        #yield scrapy.Request(self.start_urls[0], callback=self.parse)
        
            
    def parse_item_page(self, response):
        filename = 'avito' + '.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
        
        print '------------------------------------------------------'
        print 'URL:',response.url
        title = response.xpath('//h1[@itemprop="name" and @class="h1"]/text()').extract()
        assert 1==len(title)
        print 'TITLE:',title[0].encode('utf-8')
        
        # 1-к квартира, 42 м², 12/18 эт.
        # Студия, 28 м², 2/5 эт.
        # > 9-к квартира, 336 м², 23/23 эт
        m = re.search(u"(?:(\d+)-к квартира|(Студия)),\s+(\d+)\s+м²,\s+(\d+)/(\d+)\s+эт", title[0], flags=re.UNICODE)
        
        if m is not None:
            if m.group(1) is not None:
                rooms = int(m.group(1))
            else:
                rooms = 0
            m2 = Decimal(m.group(3))
            floor = int(m.group(4))
            totfloors = int(m.group(5))
        
        print 'ROOMS:',rooms.encode('utf-8')
        print 'SPACE:',m2
        print 'FLOOR:',floor,'/',totfloors
        
        price_text = response.xpath('//span[@itemprop="price"]/text()').extract()
        
        try:
            price = int(''.join(re.findall('\d+',price_text[0])))
            print 'PRICE:',price
        except ValueError as err:
            print '"%s" is not valide price: %s' % (price_text[0].encode('utf-8'), err)
            price = None
        
        city = ' '.join(response.xpath('//meta[@itemprop="addressLocality"]/@content').extract())
        print 'CITY:',city.encode('utf-8')
        district = ' '.join(response.xpath('//span[@itemprop="streetAddress"]/parent::span/text()').extract())
        print 'DISTRICT:',district.encode('utf-8')
        street = ' '.join(response.xpath('//span[@itemprop="streetAddress"]/text()').extract())
        print 'STREET:',street.encode('utf-8')
        description = ' '.join(response.xpath('//div[@class="description description-text"]/descendant::*/text()').extract())
        print 'DESC:',description.encode('utf-8')
        id = response.xpath('//div[@class="item-sku"]/span[@id="item_id"]/text()').extract()
        assert 1==len(id)
        print 'ID:','avito'+id[0].encode('utf-8')
        print '------------------------------------------------------'
        
        item = ApartmentItem()
        item['title'] = title[0]
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
        item['id'] = 'avito'+id[0]
        item['updated'] = datetime.utcnow().isoformat()
        yield item