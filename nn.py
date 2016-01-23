#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys
import pandas as pd
import skflow
from sklearn import datasets, metrics, preprocessing, cross_validation

def main():
    pd.set_option('display.encoding','utf-8')
    assert len(sys.argv) == 2
    filename = sys.argv[1]
    df = pd.read_csv(filename,encoding='utf-8',index_col=0)
    data = df[['rooms','floor','totfloors','m2','lat','lon','price']].dropna()
    print 'Data shape', data.shape

    y,X = data['price'],data[['rooms','floor','totfloors','m2','lat','lon']]
    X = preprocessing.StandardScaler().fit_transform(X)

    X_train, X_test, y_train, y_test = cross_validation.train_test_split(X, y, test_size=0.1, random_state=42)

    regressor = skflow.TensorFlowLinearRegressor()
    regressor.fit(X_train, y_train, logdir='/home/oleg/hodim/log/')
    score = metrics.mean_absolute_error(regressor.predict(X), y)
    print ("MSE: %f" % score)


if __name__ == "__main__":
    main()
