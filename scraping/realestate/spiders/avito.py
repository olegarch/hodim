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
        l.add_xpath('m2', '//h1[@itemprop="name" and @class="h1"]/text()', re=u',\s+(\d*\.\d+|\d+)\s+м²,')
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
        l.add_xpath('postDate', '//div[@class="item-subtitle"]/text()')
        l.add_xpath('postDate', '//div[contains(@class,"item-subtitle")]/text()')
        yield l.load_item()