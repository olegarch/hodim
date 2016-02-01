#!/usr/bin/env python
# -*- coding: utf8 -*-

import scrapy
from realestate.items import Apartment, ApartmentLoader
import re
from datetime import datetime
from decimal import *

class LiferealtySpider(scrapy.Spider):
    name = "liferealty"
    allowed_domains = ["life-realty.ru"]
    start_urls = (
        'http://rostov.life-realty.ru/sale/?view=simple',
    )

    def parse(self, response):
        #filename = 'liferealty' + '.html'
        #with open(filename, 'wb') as f:
        #    f.write(response.body)

        for href in response.xpath('//table[@class="list townlist"]//tr[@offerid and not(@over50)]/@offerhref').extract():
            url = response.urljoin(href)
            yield scrapy.Request(url, callback=self.parse_item_page)
            
        nexturl = response.xpath('//a[@id="nextPage"]/@href').extract()[0]
        print nexturl
        yield scrapy.Request(nexturl, callback=self.parse)
        
    def parse_item_page(self, response):
        #filename = 'liferealty' + response.url[-10:].strip('/') + '.html'
        #with open(filename, 'wb') as f:
        #    f.write(response.body)

        l = ApartmentLoader(Apartment(), response)
        l.add_value('url', response.url)
                
        type = response.xpath('//div[@id="list_sale"]/div[@class="fav"]/following-sibling::h1/text()').extract()[0]
        if u'гостинка' in type.lower():
            rooms = 0
        elif u'комната' in type.lower():
            rooms = 0
        elif u'однокомн' in type.lower():
            rooms = 1
        elif u'двухком' in type.lower():
            rooms = 2
        elif u'трехкомн' in type.lower():
            rooms = 3
        elif u'четырехко' in type.lower():
            rooms = 4
        elif u'пятикомнатна' in type.lower():
            rooms = 5
        else:
            print "ERROR type", type.encode('utf-8')
            assert False
        l.add_value('rooms',rooms)

        l.add_xpath('m2',u'//div[@id="list_sale"]/div[@class="card_block"]/p[contains(.,"Общая площадь")]/text()', re=u'Общая площадь: (\d*\.\d+|\d+) м')
        l.add_xpath('m2',u'//div[@id="list_sale"]/div[@class="card_block"]/p[contains(.,"Площадь")]/text()', re=u'Площадь: (\d*\.\d+|\d+)/(?:\d*\.\d+|\d+)/(?:\d*\.\d+|\d+) м')
        l.add_xpath('kitchenm2',u'//div[@id="list_sale"]/div[@class="card_block"]/p[contains(.,"Площадь")]/text()', re=u'Площадь: (?:\d*\.\d+|\d+)/(?:\d*\.\d+|\d+)/(\d*\.\d+|\d+) м')
        l.add_xpath('restm2',u'//div[@id="list_sale"]/div[@class="card_block"]/p[contains(.,"Площадь")]/text()', re=u'Площадь: (?:\d*\.\d+|\d+)/(\d*\.\d+|\d+)/(?:\d*\.\d+|\d+) м')
        
        l.add_xpath('floor',u'//div[@id="list_sale"]/div[@class="card_block"]/p[contains(text(),"Этаж")]/text()', re=u'Этаж: (\d+)/\d+')
        l.add_xpath('totfloors',u'//div[@id="list_sale"]/div[@class="card_block"]/p[contains(text(),"Этаж")]/text()', re=u'Этаж: \d+/(\d+)')
        
        l.add_xpath('city', u'//div[@id="list_sale"]/div[@class="card_block" and contains(.,"Местонахождение")]/text()', re=u'Населенный пункт:\s+([\w-]+)')
        l.add_xpath('district', u'//div[@id="list_sale"]/div[@class="card_block" and contains(.,"Местонахождение")]/text()', re=u'Район:\s+(\w+)')
        l.add_xpath('street', u'//div[@id="list_sale"]/div[@class="card_block" and contains(.,"Местонахождение")]/text()', re=u'Адрес:\s+(.*)')
        
        l.add_xpath('rennovation',u'//div[@id="list_sale"]/div[@class="card_block" and contains(.,"Параметры")]/descendant-or-self::*/text()',re=u'Состояние помещения:\s+(.*)')
        l.add_xpath('walls',u'//div[@id="list_sale"]/div[@class="card_block" and contains(.,"Параметры")]/descendant-or-self::*/text()',re=u'Тип дома:\s+(.*)')
        l.add_xpath('balcony',u'//div[@id="list_sale"]/div[@class="card_block" and contains(.,"Параметры")]/descendant-or-self::*/text()',re=u'Балкон:\s+(.*)')
        l.add_xpath('wc',u'//div[@id="list_sale"]/div[@class="card_block" and contains(.,"Параметры")]/descendant-or-self::*/text()',re=u'Санузел:\s+(.*)')
        
        l.add_xpath('description', u'//div[@id="list_sale"]/div[@class="card_block" and contains(.,"Дополнительная")]/descendant-or-self::*/text()')
        
        l.add_value('updated', datetime.utcnow().isoformat())
        l.add_xpath('postDate',u'//div[@id="list_sale"]//div[@class="card_date" and contains(.,"добавлено")]/descendant-or-self::*/text()',re=u'добавлено\s+(.*)')
        
        price = ''.join(response.xpath(u'//div[@id="list_sale"]//div[@class="card_price" and contains(.,"руб")]/text()').extract())
        self.logger.debug("1. price "+str(price))
        price = ''.join(price)
        self.logger.debug("2. price "+price)
        price = price.replace(',','.')
        self.logger.debug("3. price "+price)
        price = str(int(float(price)*1000))
        self.logger.debug("4. price "+price)
        l.add_value('price',price)
        
        yield l.load_item()
