from collections import OrderedDict
import re
import math
from string import digits
import string
import dill
import csv

relevanceJudgements = {}
featureMatrix = OrderedDict()
qrelDocIDs = []

V = 0
cTF = []
bm25Scores = {}
jmScores = {}
lScores = {}
oTFScores = {}
tfIDFScores = {}
bm25Scores1000 = {}
jmScores1000 = {}
lScores1000 = {}
oTFScores1000 = {}
tfIDFScores1000 = {}
docIDLst = {}

f = open('totalTF.p', 'rb')
cTF = dill.load(f)
f.close()
V = len(cTF)

relevance = {}

def getRevelanceJudgements(qrel):
    with open(qrel, 'r') as f:
        for judgement in f:
            cols = judgement.strip().split()
            if len(cols) < 4:
                continue
            queryID = cols[0]
            documentID = cols[2]
            score = int(cols[3])
            if queryID in relevance:
                relevance[queryID][documentID] = score
            else:
                relevance[queryID] = {}
                relevance[queryID][documentID] = score
            qrelDocIDs.append(documentID)
            if queryID in relevanceJudgements:
                relevanceJudgements[queryID].append((documentID, 'na'))
            else:
                relevanceJudgements[queryID] = [(documentID, 'na')]

def getDocScoreFromRM(rmFile, ds):
    with open(rmFile, 'r') as f:
        for res in f:
            cols = res.strip().split()
            if len(cols) < 5:
                continue
            queryID = cols[0]
            documentID = cols[2]
            score = cols[4]
            qrelDocIDs.append(documentID)
            if queryID in ds:
                ds[queryID].append((documentID, score))
            else:
                ds[queryID] = [(documentID, score)]

def get1000Scores(ds, opt=0):
    ds1000 = {}
    for qID in relevanceJudgements:
        if qID in ds:
            ds1000[qID] = []
            if opt != 0:
                docIDLst[qID] = []
            for docScorePair in relevanceJudgements[qID]:
                if opt != 0:
                    docIDLst[qID].append(docScorePair[0])
                    pair = [item for item in ds[qID] if item[0] == docScorePair[0]]
                    score = pair[0][1] if pair else ''
                    ds1000[qID].append((docScorePair[0], score))
                else:
                    if docScorePair[0] in docIDLst[qID]:
                        pair = [item for item in ds[qID] if item[0] == docScorePair[0]]
                        score = pair[0][1] if pair else ''
                        ds1000[qID].append((docScorePair[0], score))
            if len(ds1000[qID]) < 1000:
                ds[qID].reverse()
                limit = len(ds1000[qID])
                for docScorePair in ds[qID]:
                    if limit < 1000:
                        pair = [item for item in ds1000[qID] if item[0] == docScorePair[0]]
                        if pair:
                            continue
                        if opt != 0:
                            docIDLst[qID].append(docScorePair[0])
                            ds1000[qID].append(docScorePair)
                            limit += 1
                        else:
                            if docScorePair[0] in docIDLst[qID]:
                                ds1000[qID].append(docScorePair)
                                limit += 1
                    else:
                        break
            print(len(docIDLst[qID]))
    return ds1000

def generateScores(ds1000, model):
    ds1000Temp = {}
    for qid in ds1000:
        ds1000Temp[qid] = []
        for docScorePair in ds1000[qid]:
            pair = [item for item in ds1000[qid] if item[0] == docScorePair[0]][0][1]
            if pair == '':
                pair = 0
            ds1000Temp[qid].append((docScorePair[0], pair))
    return ds1000Temp

def validateDS(ds1000):
    for qid in ds1000:
        for docScorePair in ds1000[qid]:
            if docScorePair[0] not in docIDLst[qid]:
                print('Mismatch! ', str(qid), docScorePair[0])

def createFeatureMatrix(ds1000, model, opt=0):
    for qID in ds1000:
        for docScorePair in ds1000[qID]:
            if docScorePair[0] in relevance[qID]:
                label = relevance[qID][docScorePair[0]]
            else:
                label = 0
            identifier = str(qID) + '-' + docScorePair[0]
            if opt != 0:
                featureMatrix[identifier] = OrderedDict()
                featureMatrix[identifier][model] = [docScorePair[1], label]
            else:
                if identifier in featureMatrix:
                    featureMatrix[identifier][model] = [docScorePair[1], label]

def staticFeatureMatrixCSV():
    with open('staticFeatureMatrix.csv', 'w', newline='') as csvfile:
        filewriter = csv.writer(csvfile)
        filewriter.writerow(['QID-DocID', 'TF-IDF', 'Okapi TF', 'BM25', 'Laplace', 'Jelinek-Mercer', 'Label'])
        for identifier in featureMatrix:
            tfIDF = oTF = bm25 = l = jm = ''
            label = 0
            for model in featureMatrix[identifier]:
                score = featureMatrix[identifier][model][0]
                label = featureMatrix[identifier][model][1]
                if model == 'BM25':
                    bm25 = score
                elif model == 'TF-IDF':
                    tfIDF = score
                elif model == 'Okapi TF':
                    oTF = score
                elif model == 'Jelinek-Mercer':
                    jm = score
                elif model == 'Laplace':
                    l = score
            filewriter.writerow([identifier, tfIDF, oTF, bm25, l, jm, label])

def main():
    getRevelanceJudgements("cranqrel.trec.txt")

    getDocScoreFromRM("../HW1/bm25.txt", bm25Scores)
    getDocScoreFromRM("../HW1/jm.txt", jmScores)
    getDocScoreFromRM("../HW1/laplace.txt", lScores)
    getDocScoreFromRM("../HW1/okapi.txt", oTFScores)
    getDocScoreFromRM("../HW1/tfidf.txt", tfIDFScores)

    bm25Scores1000 = get1000Scores(bm25Scores, 1)
    jmScores1000 = get1000Scores(jmScores)
    lScores1000 = get1000Scores(lScores)
    oTFScores1000 = get1000Scores(oTFScores)
    tfIDFScores1000 = get1000Scores(tfIDFScores)

    bm25Scores1000Scored = generateScores(bm25Scores1000, 'BM25')
    jmScores1000Scored = generateScores(jmScores1000, 'Jelinek-Mercer')
    lScores1000Scored = generateScores(lScores1000, 'Laplace')
    oTFScores1000Scored = generateScores(oTFScores1000, 'Okapi TF')
    tfIDFScores1000Scored = generateScores(tfIDFScores1000, 'TF-IDF')

    validateDS(bm25Scores1000Scored)
    validateDS(jmScores1000Scored)
    validateDS(lScores1000Scored)
    validateDS(oTFScores1000Scored)
    validateDS(tfIDFScores1000Scored)

    createFeatureMatrix(tfIDFScores1000Scored, 'TF-IDF', 1)
    createFeatureMatrix(oTFScores1000Scored, 'Okapi TF')
    createFeatureMatrix(bm25Scores1000Scored, 'BM25')
    createFeatureMatrix(lScores1000Scored, 'Laplace')
    createFeatureMatrix(jmScores1000Scored, 'Jelinek-Mercer')

    staticFeatureMatrixCSV()
    print("Done! staticFeatureMatrix.csv created.")

main()
