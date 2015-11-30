#!/usr/bin/env python
# -*- coding: utf8 -*-

import scrapy
from avito.items import ApartmentItem
import re
from datetime import datetime
from decimal import *

def containingClass(className):
  return "contains(concat(' ',normalize-space(@class),' '),' " + className + " ')"

class IrrSpider(scrapy.Spider):
    name = "irr"
    allowed_domains = ["irr.ru"]
    start_urls = [
        "http://rostovnadonu.irr.ru/real-estate/apartments-sale/",
    ]
    custom_settings = {
        'COOKIES_ENABLED': True
    }    

    def parse(self, response):     
        filename = 'irr' + '.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
            
        for href in response.xpath('//a[contains(@class,"productBlock")]/@href').extract():
            url = response.urljoin(href)
            self.logger.info('crawling %s',url)
            yield scrapy.Request(url, callback=self.parse_item_page)
            
        next_page_href = response.xpath(u"//link[@rel='next']/@href").extract()[0]
        next_url = response.urljoin(next_page_href)
        self.logger.info('crawling next %s',next_url)
        yield scrapy.Request(next_url, callback=self.parse)
    
    def extract_property(self, response, propertyName):
        propertyVal = response.xpath(u'//div[@class="propertyName" and contains(text(),"'+propertyName+'")]/following-sibling::div[@class="propertyValue"]/descendant-or-self::*/text()').extract()
        self.logger.info('property %s %s', propertyName, propertyVal)
        return propertyVal[0].strip()
            
    def parse_item_page(self, response):
        item = ApartmentItem()
        
        filename = response.url[-10:] + '.html'
        self.logger.info('filename %s',filename)
        with open(filename, 'wb') as f:
            f.write(response.body)

        self.logger.info('===================================================================')
        item['url'] = response.url
        self.logger.info('URL %s',item['url'])
        s = response.xpath('//i[contains(@class,"irri-map")]/following-sibling::span/text()').extract()
        if len(s)==0:
            s = response.xpath('//i[contains(@class,"icon_spot")]/following-sibling::div/text()').extract()
            
        #item['id'] ='irr'+ response.xpath('//inputa[@type="hidden" and @class="js-advertId"]/@value').extract()[0]
        item['street'] = ' '.join(s)
        item['floor'] = int(self.extract_property(response,u"Этаж:"))
        item['totfloors'] = int(self.extract_property(response,u"Этажей в здании:"))
        #item['kitchenm2'] = Decimal( self.extract_property(response,u"Площадь кухни:").split()[0] )
        item['restm2'] = Decimal( self.extract_property(response,u"Жилая площадь:").split()[0] )
        #item['wc'] = self.extract_property(response,u"Санузел:")
        #item['walls'] = self.extract_property(response,u"Материал стен:")
        #item['ceilings'] = self.extract_property(response,u"Высота потолков:")
        item['rooms'] = int(self.extract_property(response,u"Комнат в квартире:"))
        item['m2'] = Decimal( self.extract_property(response,u"Общая площадь:").split()[0] )
        #item['district'] = self.extract_property(response,u"Район города:")
        #item['rennovation'] = self.extract_property(response,u"Ремонт:")
        #item['builtDate'] = self.extract_property(response,u"Год постройки:")
        #item['water'] = self.extract_property(response,u"Система водоснабжения:")
        #item['heating'] = self.extract_property(response,u"Система отопления:")
        item['description'] = ' '.join([t.strip() for t in response.xpath('//div[@class="advertDescriptionText"]/text()').extract()])
        item['updated'] = datetime.utcnow().isoformat()
        self.logger.info('===================================================================')
        
        #yield item
        return 
        
        item['title'] = title[0]
        item['district'] = district
        item['city'] = city
        item['price'] = price

        yield item