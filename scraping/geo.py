#!/usr/bin/env python
# -*- coding: utf8 -*-
#google_api_key = "AIzaSyAZVa_DBWv0uQ_m6-UgWTToYAY6wnA2EiQ"

import geopy
from geopy.geocoders import Nominatim, GoogleV3, Bing, Yandex

#geolocator = Bing()
#geolocator = Nominatim()
#geolocator = GoogleV3(domain = 'maps.googleapis.com')
geolocator = Yandex()
#location = geolocator.geocode(u"ул. Юпитера д.1 Ростов")
#location = geolocator.geocode(u"улица Мурлычева, 30/28,р-н Пролетарский, ,Ростов-на-Дону")
#location = geolocator.geocode(u"Ленина 42  Ростов")
#location = geolocator.geocode(u"Турмалиновская 62 Ростов")
#location = geolocator.geocode(u"Красноармейская, 200/1, Ростов-на-Дону")
try:
    location = geolocator.geocode(u"Королева/Беляева, ЦЕНА СНИЖЕНА!!! 46м2, р-н Ворошиловский, Ростов-на-Дону",timeout=0.1)
except geopy.exc.GeocoderTimedOut as e:
    print("Error: geocode failed with message '%s'"%(e.message))
    location = geolocator.geocode(u"Королева/Беляева, ЦЕНА СНИЖЕНА!!! 46м2, р-н Ворошиловский, Ростов-на-Дону",timeout=0.10)
    
print location.address.encode('utf-8')
print (location.latitude, location.longitude)
print repr(location.raw).decode("unicode-escape").encode('utf-8')
print location.raw[u'metaDataProperty'][u'GeocoderMetaData'][u'precision']