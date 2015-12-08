#!/usr/bin/env python
# -*- coding: utf8 -*-

import scrapy
from realestate.items import Apartment, ApartmentLoader
import re
from datetime import datetime
from decimal import *

def containingClass(className):
  return "contains(concat(' ',normalize-space(@class),' '),' " + className + " ')"

class IrrSpider(scrapy.Spider):
    name = "irr"
    allowed_domains = ["irr.ru"]
    #start_urls = [ "http://rostovnadonu.irr.ru/real-estate/apartments-sale/" ]
    start_urls = [ "http://rostovnadonu.irr.ru/real-estate/apartments-sale/search/page_len60/" ]
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
            
    def extract_property_string(self, propertyName):
        return u'//div[@class="propertyName" and contains(text(),"'+propertyName+'")]/following-sibling::div[@class="propertyValue"]/descendant-or-self::*/text()'
            
    def parse_item_page(self, response):

        filename = 'irr' + response.url[-10:] + '.html'
        self.logger.info('filename %s',filename)
        with open(filename, 'wb') as f:
            f.write(response.body)
    
        l = ApartmentLoader(Apartment(), response)
        l.add_value('url', response.url)
        #l.add_xpath('description', '//div[@class="advertDescriptionText"]/text()')
        l.add_xpath('description', '//meta[@name="description"]/@content')
        l.add_xpath('street', '//i[contains(@class,"irri-map")]/following-sibling::span/text()')
        l.add_xpath('street', '//i[contains(@class,"icon_spot")]/following-sibling::div/text()')
        l.add_xpath('price', '//div[contains(@class,"productPagePrice")]/text()')
        #l.add_value('city', u'Ростов-на-Дону')
        l.add_value('updated', datetime.utcnow().isoformat())
        l.add_xpath('postDate', '//div[@class="advertHeader"]/div[@class="createDate"]/text()')
        l.add_xpath('postDate', '//div[@class="productPage_headerColumn"]/div[@class="productPage__createDate"]/text()')

        # properties
        l.add_xpath('m2', self.extract_property_string(u"Общая площадь:"))
        l.add_xpath('kitchenm2', self.extract_property_string(u"Площадь кухни:"))
        l.add_xpath('restm2', self.extract_property_string(u"Жилая площадь:"))
        
        l.add_xpath('floor', self.extract_property_string(u"Этаж:"))
        l.add_xpath('totfloors', self.extract_property_string(u"Этажей в здании:"))
        l.add_xpath('rooms', self.extract_property_string(u"Комнат в квартире:"))
        
        l.add_xpath('district', self.extract_property_string(u"Район города:"))
        l.add_xpath('rennovation', self.extract_property_string(u"Ремонт:"))
        l.add_xpath('builtDate', self.extract_property_string(u"Год постройки:"))
        l.add_xpath('water', self.extract_property_string(u"Система водоснабжения:"))
        l.add_xpath('heating', self.extract_property_string(u"Система отопления:"))
        l.add_xpath('wc', self.extract_property_string(u"Санузел:"))
        l.add_xpath('walls', self.extract_property_string(u"Материал стен:"))
        l.add_xpath('ceilings', self.extract_property_string(u"Высота потолков:"))
        l.add_xpath('balcony', self.extract_property_string(u"Балкон"))
        l.add_xpath('security', self.extract_property_string(u"Охрана"))
        yield l.load_item()
