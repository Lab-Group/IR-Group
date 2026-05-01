import numpy as np
import pandas
from sklearn import linear_model, model_selection, preprocessing
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score
from sklearn.feature_selection import SelectKBest, f_classif
import csv
from collections import OrderedDict
from operator import itemgetter


def getNGrams(file):
    colNames = []
    with open(file, "r") as nGramFile:
        for nGram in nGramFile.readlines():
            colNames.append(nGram.strip())
    return colNames

def getBestFeatures(X, y, csvFile, names):
    selector = SelectKBest(f_classif, k=10)
    selector.fit_transform(X, y)
    dataset = pandas.read_csv(csvFile, names=names)
    feat_names = dataset.columns[0:len(names)-1].values[selector.get_support()]
    scores = selector.scores_[selector.get_support()]
    ns_df = pandas.DataFrame(list(zip(feat_names, scores)), columns=['Feat_names', 'F_Scores'])
    print(ns_df.sort_values(['F_Scores', 'Feat_names'], ascending=[False, True]))

def getAccuracy(txtFile, csvFile):
    df = pandas.read_csv(csvFile, skipinitialspace=True, usecols=['DocID'])
    dID = df.values
    names = getNGrams(txtFile)
    dataset = pandas.read_csv(csvFile, names=names, skiprows=[0])
    for name in names:
        if dataset[name].notnull().sum() == 0:
            dataset[name] = 0
    array = dataset.values
    lenNGrams = len(names) - 1
    X = array[:, 0:lenNGrams]
    Y = array[:, lenNGrams]
    le = preprocessing.LabelEncoder()
    Y = le.fit_transform(Y)
    imputer = SimpleImputer()
    X = imputer.fit_transform(X)
    kfold = model_selection.KFold(n_splits=5, random_state=None, shuffle=False)
    train, test = next(kfold.split(X, Y))
    regr = linear_model.LogisticRegression(max_iter=1000)
    regr.fit(X[train], Y[train])
    predictions = regr.predict(X[test])
    print("Accuracy: %.2f%%" % (accuracy_score(Y[test], predictions) * 100))
    getBestFeatures(X, Y, csvFile, names)

def main():
    getAccuracy('scratch.txt', 'staticFeatureMatrixFull200.csv')

main()
