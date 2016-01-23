#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys
#import numpy as np
#import matplotlib.pyplot as plt

import pandas as pd
from pandas.io import sql
from sqlalchemy import create_engine

def preprocess_data(X, scaler=None):
  if not scaler:
    scaler = StandardScaler()
    scaler.fit(X)
  X = scaler.transform(X)
  return X, scaler
  
def read():
    pd.set_option('display.encoding','utf-8')
    
    engine = create_engine('mysql+mysqldb://scrapyuser:1234@ec2-52-28-88-160.eu-central-1.compute.amazonaws.com:3306/testdb?charset=utf8', echo=True)
    df = sql.read_sql_query("SELECT url, rooms, floor, totfloors, m2, kitchenm2, restm2, "
                            "wc, walls, ceilings, rennovation, builtdate, heating, "
                            "water, balcony, security, "
                            "x(location) as lat, y(location) as lon, price "
                            "FROM realestate "
                            #"WHERE security IS NOT NULL "
                            #"LIMIT 10"
                            ,engine)
    print df.shape
    
    df.loc[(df.balcony == u'есть')|(df.balcony == u'да'),'balcony'] = 1
    df.loc[df.balcony == u'нет','balcony'] = -1
    df.loc[df.balcony.isnull(),'balcony'] = 0

    #df.loc[(df.security == u'есть')|(df.security == u'да'),'security'] = 1
    #df.loc[df.security.isnull(),'security'] = 0

    # панельный - 1; кирпичный - 2; монолит - 3
    #df.loc[(df.walls == u'панельный')|(df.security == u'да'),'security'] = 1
    
    print df
    df.to_csv('data.csv', sep=',', encoding='utf-8', index=True)

def main():
    read()

if __name__ == "__main__":
    main()
