import pandas
from sklearn import model_selection
from sklearn import linear_model
from operator import itemgetter

def createDict(qdIDTest, predictions):
    testDict = {}
    i = 0
    for prediction in predictions:
        qdIDVal = qdIDTest[i][0]
        i += 1
        qID = qdIDVal.split('-', 1)[0]
        docID = qdIDVal.split('-', 1)[1]
        if qID in testDict:
            testDict[qID].append((docID, prediction))
        else:
            testDict[qID] = []
            testDict[qID].append((docID, prediction))
    return testDict

def sortDict(testDict):
    for item in testDict:
        sorted_list = sorted(testDict[item], key=itemgetter(1), reverse=True)
        testDict[item] = sorted_list
    return testDict

def createPerformanceFile(testDict):
    with open('trainingperformance.txt', 'a') as f:
        for item in testDict:
            i = 0
            for docScorePair in testDict[item]:
                i += 1
                f.write("%s Q0 %s %d %f Exp\n" % (item, docScorePair[0], i, docScorePair[1]))

def main():
    qID_docID = ['QID-DocID']

    df = pandas.read_csv('staticFeatureMatrix.csv', skipinitialspace=True, usecols=qID_docID)
    df_array = df.values
    qdID = df_array

    names = ['TF-IDF', 'Okapi TF', 'BM25', 'Laplace', 'Jelinek-Mercer', 'Label']
    dataset = pandas.read_csv('staticFeatureMatrix.csv', names=names, skiprows=[0])
    dataset = dataset.fillna(0)
    array = dataset.values
    X = array[:, 0:5]
    Y = array[:, 5]

    kfold = model_selection.KFold(n_splits=5, random_state=None, shuffle=False)
    for train, test in kfold.split(X, Y):
        qdIDTest = qdID[train]
        regr = linear_model.LinearRegression()
        regr.fit(X[train], Y[train])
        predictions = regr.predict(X[train])

        testDict = createDict(qdIDTest, predictions)
        testDict = sortDict(testDict)
        createPerformanceFile(testDict)

    print("Done! trainingperformance.txt created.")

main()
