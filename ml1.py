#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys
import numpy as np
import matplotlib.pyplot as plt
from sklearn import linear_model
from sklearn import tree
from sklearn import ensemble
from sklearn import preprocessing
from sklearn.cross_validation import train_test_split, cross_val_score, cross_val_predict
from sklearn.pipeline import make_pipeline

assert len(sys.argv) == 2
filename = sys.argv[1]

f = open(filename)
titles = f.readline().strip('\n').split(',')  # skip the header
# rooms,floor,totfloors,m2,price,lon,lat
#data = np.loadtxt(f, delimiter=',', dtype = {'names' : titles, 'formats':['u8','u8','u8','f2','u4','S32','S32']})

data = np.loadtxt(f, delimiter=',', usecols=(0,1,2,3,4,5,6))
#data = data[:1000,:]
print data
print data.shape

#data = data[data[:,3].argsort()]
#titles = titles[2:4]
X = data[:,:-1]
#X = X.reshape((len(X),1))
y = data[:,-1]
#X = preprocessing.scale(X)
#regr_2 = AdaBoostRegressor(DecisionTreeRegressor(max_depth=4),
#                          n_estimators=300, random_state=rng)
rng = np.random.RandomState(41)

regressions = [
    ("Tree", tree.DecisionTreeRegressor()),
    ("RFTree", ensemble.RandomForestRegressor(n_estimators=30, random_state=rng)),
    ("AdaBoostTree", ensemble.AdaBoostRegressor(tree.DecisionTreeRegressor(), n_estimators=300, random_state=rng)),
    ("OLS", linear_model.LinearRegression()),
    ("Ridge8", linear_model.Ridge(alpha=.99)),
    #("Ridge1", linear_model.Ridge(alpha=.1)),
    ("Lasso", linear_model.Lasso(alpha = 0.1)),
    ("ScaledOLS", make_pipeline(preprocessing.StandardScaler(), linear_model.LinearRegression()))
]


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.01, random_state = rng)
X_test_sorted = X_test[X_test[:,-1].argsort()]

print X_train.shape
print X_test.shape

plt.figure()
plt.scatter(X_test[:,-1], y_test,  color='black')


for name, regr_non_scaled in regressions:
    regr = make_pipeline(preprocessing.StandardScaler(), regr_non_scaled)
    regr.fit(X_train, y_train)
    scores = cross_val_score(regr, X, y, cv=3)
    score = regr.score(X_test, y_test)
    #predict = cross_val_predict(regr, X, y, cv=3)
    predict = regr.predict(X_test)
    print("%s accuracy: %0.2f (+/- %0.2f)" % (name, scores.mean(), scores.std() * 2))
    #print("%s accuracy: %0.2f" % (name, score))
    #print(name+' coefficients: \n', regr_non_scaled.coef_)
    #print(name+' intercept: \n', regr.intercept_)
    #plt.plot(X_test_sorted[:,-1], regr.predict(X_test_sorted),  linewidth=3)
    plt.plot(X_test[:,-1], predict,  '.', label=name)
    
    if hasattr(regr_non_scaled,'feature_importances_'):
        importances = regr_non_scaled.feature_importances_
        for f in range(X.shape[1]):
            print("feature '%s' importance (%f)" % (titles[f], importances[f]))


plt.legend(loc="upper right")
#plt.xticks(())
#plt.yticks(())
plt.show()
exit(0)


# The coefficients
# print('Coefficients: \n', regr.coef_)
# The mean square error
print("Residual sum of squares: %.2f"
      % np.mean((regr.predict(X_test) - y_test) ** 2))

# Explained variance score: 1 is perfect prediction
print('Variance score: %.2f' % regr.score(X_test, y_test))

# Plot outputs
print X_test
X_test_sorted = X_test[X_test[:,-1].argsort()]
print X_test

plt.plot(X_test_sorted[:,-1], regr.predict(X_test_sorted), color='blue', linewidth=3)

