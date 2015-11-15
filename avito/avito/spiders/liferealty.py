#!/usr/bin/env python
# -*- coding: utf8 -*-

import scrapy
from avito.items import ApartmentItem
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
    
        filename = 'liferealty' + '.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
            
        nexturl = response.xpath('//a[@id="nextPage"]/@href').extract()[0]
        print nexturl
        yield scrapy.Request(nexturl, callback=self.parse)
            
        for el in response.xpath('//table[@class="list townlist"]//tr[@offerid and not(@over50)]'):

            item = ApartmentItem()
            item['id'] = 'liferealty' + el.xpath('@offerid').extract()[0]
            item['url'] = el.xpath('@offerhref').extract()[0]
                        
            print item['url']
            item['title'] = el.xpath('.//td[@class="txt"]/a/text()').extract()[0]
            type = el.xpath('.//td[@class="txt"]/a/text()').extract()[0]
            if u'гостинка' in type.lower():
                item['rooms'] = 0
            elif u'комната' in type.lower():
                item['rooms'] = 0
            elif u'однокомн' in type.lower():
                item['rooms'] = 1
            elif u'двухком' in type.lower():
                item['rooms'] = 2
            elif u'трехкомн' in type.lower():
                item['rooms'] = 3
            elif u'четырехко' in type.lower():
                item['rooms'] = 4
            elif u'пятикомнатна' in type.lower():
                item['rooms'] = 5
            else:
                print "ERROR type", type.encode('utf-8')
                assert False

            item['city'] = u'Ростов-на-Дону'
            item['district'] = el.xpath('.//td[@class="price"]/following-sibling::td[@class="mini"]/div/descendant-or-self::*/text()').extract()[0]
            print item['district'].encode('utf-8')
            item['street'] = ""
            for i in el.xpath(u'.//span[@class="mini" and contains(text(),"Адрес")]/text()').extract():
                item['street'] = i[7:]
            
            item['m2'] = Decimal(el.xpath('.//td[@class="txt"]/following-sibling::td[@class="aright"][1]/descendant-or-self::*/text()').extract()[0])
            print item['m2'], str(item['m2']), repr(item['m2'])
            try:
                item['restm2'] = Decimal(el.xpath('.//td[@class="txt"]/following-sibling::td[@class="aright"][2]/descendant-or-self::*/text()').extract()[0])
                item['kitchenm2'] = Decimal(el.xpath('.//td[@class="txt"]/following-sibling::td[@class="aright"][3]/descendant-or-self::*/text()').extract()[0])
            except InvalidOperation as err:
                print "error: m2 for kitchen or rest is not given:", err
                
            price = ''.join(el.xpath('.//td[@class="price"]/span/text()').extract())
            item['price'] = int(''.join(re.findall('\d+',price)))*1000
            #print item['price']
            #print item['m2'], item['kitchenm2'], item['restm2']
            item['description'] = ' '.join(el.xpath('.//td[@class="txt"]/descendant-or-self::*/text()').extract())
            
            m = re.search(u'этаж\s+(\d+)/(\d+)',item['description'])
            #print m.group(0).encode('utf-8')
            item['floor'] = int(m.group(1))
            item['totfloors'] = int(m.group(2))
            item['description'] = ''
            
            tmp = ' '.join(el.xpath('.//td[@class="txt"]/descendant-or-self::*/text()').extract())            
            
            item['updated'] = datetime.utcnow().isoformat()
            print repr(dict(item)).decode("unicode-escape").encode('utf-8') + "\n"
            yield item

