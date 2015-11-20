#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys
import numpy as np
import matplotlib.pyplot as plt
from sklearn import linear_model
from sklearn import tree
from sklearn import ensemble
from sklearn import preprocessing
from sklearn import neighbors
from sklearn import gaussian_process
from sklearn import svm
from sklearn.cross_validation import train_test_split, cross_val_score, cross_val_predict, ShuffleSplit
from sklearn.pipeline import make_pipeline
from sklearn.learning_curve import learning_curve
from sklearn import gaussian_process

def plot_learning_curve(estimator, title, X, y, ylim=None, cv=None,
                        n_jobs=1, train_sizes=np.linspace(.1, 1.0, 5)):
    """
    Generate a simple plot of the test and traning learning curve.

    Parameters
    ----------
    estimator : object type that implements the "fit" and "predict" methods
        An object of that type which is cloned for each validation.

    title : string
        Title for the chart.

    X : array-like, shape (n_samples, n_features)
        Training vector, where n_samples is the number of samples and
        n_features is the number of features.

    y : array-like, shape (n_samples) or (n_samples, n_features), optional
        Target relative to X for classification or regression;
        None for unsupervised learning.

    ylim : tuple, shape (ymin, ymax), optional
        Defines minimum and maximum yvalues plotted.

    cv : integer, cross-validation generator, optional
        If an integer is passed, it is the number of folds (defaults to 3).
        Specific cross-validation objects can be passed, see
        sklearn.cross_validation module for the list of possible objects

    n_jobs : integer, optional
        Number of jobs to run in parallel (default 1).
    """
    plt.figure()
    plt.title(title)
    if ylim is not None:
        plt.ylim(*ylim)
    plt.xlabel("Training examples")
    plt.ylabel("Score")
    scoring = None#'mean_squared_error'
    train_sizes, train_scores, test_scores = learning_curve(
        estimator, X, y, cv=cv, n_jobs=n_jobs, train_sizes=train_sizes, scoring=scoring)
    print train_scores
    train_scores_mean = np.mean(train_scores, axis=1)
    train_scores_std = np.std(train_scores, axis=1)
    test_scores_mean = np.mean(test_scores, axis=1)
    test_scores_std = np.std(test_scores, axis=1)
    if scoring == 'mean_squared_error':
        train_scores_mean = -train_scores_mean
        test_scores_mean = -test_scores_mean
    plt.grid()

    plt.fill_between(train_sizes, train_scores_mean - train_scores_std,
                     train_scores_mean + train_scores_std, alpha=0.1,
                     color="r")
    plt.fill_between(train_sizes, test_scores_mean - test_scores_std,
                     test_scores_mean + test_scores_std, alpha=0.1, color="g")
    plt.plot(train_sizes, train_scores_mean, 'o-', color="r",
             label="Training score")
    plt.plot(train_sizes, test_scores_mean, 'o-', color="g",
             label="Cross-validation score")

    plt.legend(loc="best")
    return plt
    
def main():

    assert len(sys.argv) == 2
    filename = sys.argv[1]

    f = open(filename)
    titles = f.readline().strip('\n').split(',')  # skip the header
    # rooms,floor,totfloors,m2,price,lon,lat
    #data = np.loadtxt(f, delimiter=',', dtype = {'names' : titles, 'formats':['u8','u8','u8','f2','u4','S32','S32']})

    #data = np.loadtxt(f, delimiter=',', usecols=(0,1,2,3,4,5,6))
    data = np.loadtxt(f, delimiter=',', usecols=(0,1,2,3,4))
    #data = data[:10,:]
    print data
    print data.shape

    #data = data[data[:,3].argsort()]
    titles = titles[:-1]
    X = data[:,:-1]
    print X
    print X.shape
    #exit(0)
    y = data[:,-1]
    #X = preprocessing.scale(X)
    #regr_2 = AdaBoostRegressor(DecisionTreeRegressor(max_depth=4),
    #                          n_estimators=300, random_state=rng)
    rng = np.random.RandomState(41)

    regressions = [
        #("GaussianProcess(regr='constant',corr='cubic')",gaussian_process.GaussianProcess(regr='constant',corr='cubic', theta0=1e-2, thetaL=1e-4, thetaU=1e-1,random_start=100)),
        #("GaussianProcess(regr='constant',corr='squared_exponential')",gaussian_process.GaussianProcess(regr='constant',corr='squared_exponential', theta0=1e-1, thetaL=1e-3, thetaU=1,random_start=100)),
        ("LinearSVR",svm.LinearSVR()),
        #("SVR",svm.SVR()),
        ("SVR(kernel='linear')",svm.SVR(kernel='linear')),
        ("SVR(C=10.0, kernel='linear')",svm.SVR(C=10.0,kernel='linear')),
        #("SVR(C=1.0, epsilon=0.2)",svm.SVR(C=1.0, epsilon=0.2)),
        #("SVR(C=1.0, epsilon=0.4)",svm.SVR(C=1.0, epsilon=0.4)),
        #("SVR(kernel='rbf', gamma=0.7)",svm.SVR(kernel='rbf', gamma=0.7)),
        #("NuSVR",svm.NuSVR()),
        #("GradientBoostingRegressor",ensemble.GradientBoostingRegressor()),
        #("KNeighborsRegressor(k=2,weights='uniform')", neighbors.KNeighborsRegressor(n_neighbors=2, weights='uniform')),
        #("KNeighborsRegressor(k=5,weights='uniform')", neighbors.KNeighborsRegressor(n_neighbors=5, weights='uniform')),
        #("KNeighborsRegressor(k=10,weights='uniform')", neighbors.KNeighborsRegressor(n_neighbors=10, weights='uniform')),
        #("KNeighborsRegressor(k=5,weights='distance')", neighbors.KNeighborsRegressor(n_neighbors=5, weights='distance')),
        #("Tree", tree.DecisionTreeRegressor()),
        #("RFTree", ensemble.RandomForestRegressor(n_estimators=100, random_state=rng)),
        #("AdaBoostTree", ensemble.AdaBoostRegressor(tree.DecisionTreeRegressor(), n_estimators=300, random_state=rng)),
        ("OLS", linear_model.LinearRegression()),
        #("Ridge8", linear_model.Ridge(alpha=.99)),
        #("Ridge1", linear_model.Ridge(alpha=.1)),
        #("Lasso", linear_model.Lasso(alpha = 0.1)),
        #("ScaledOLS", make_pipeline(preprocessing.StandardScaler(), linear_model.LinearRegression()))
    ]


    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.01, random_state = rng)
    X_test_sorted = X_test[X_test[:,-1].argsort()]

    #print X_train.shape
    #print X_test.shape

    estimator = linear_model.LinearRegression()
    #plot_learning_curve(regressions[0][1], regressions[0][0], X, y, ylim=(0.7, 1.01), cv=cv, n_jobs=4)
    for name, model_raw in regressions:
        cv = ShuffleSplit(X.shape[0], n_iter=5, test_size=0.2, random_state=0)
        model = make_pipeline(preprocessing.StandardScaler(), model_raw)
        #model = make_pipeline(preprocessing.MinMaxScaler(), model_raw)
        #model = make_pipeline(preprocessing.RobustScaler(), model_raw)
        #plot_learning_curve(model, name, X, y, ylim=(0, 1.01), cv=cv, n_jobs=7)
        plot_learning_curve(model, name, X, y, cv=cv, n_jobs=8)
    plt.show()
    exit(0)

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

if __name__ == "__main__":
    main()
