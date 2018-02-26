import json
import pandas as pd
from os import path
from sklearn import preprocessing


from metalearn.features.metafeatures import MetaFeatures
with open('/home/rlaboulaye/Downloads/dataSchema.json', "r") as f:
    datasetSchema = json.load(f)
dataRoot = '/home/rlaboulaye/Downloads/'
testData = pd.read_csv( path.join(dataRoot, 'trainData.csv.gz'), header=0).fillna('0').replace('', '0')
testTargets = pd.read_csv( path.join(dataRoot, 'trainTargets.csv.gz'), header=0).fillna('0').replace('', '0')

testDataCatLabels = []
testDataLabelEncoders = dict()

for colDesc in datasetSchema['trainData']['trainData']:

    if colDesc['varType']=='categorical':
        testDataCatLabels.append(colDesc['varName'])
        testDataLabelEncoders[colDesc['varName']] = preprocessing.LabelEncoder().fit(testData[colDesc['varName']])
        testData[colDesc['varName']] = testDataLabelEncoders[colDesc['varName']].transform(testData[colDesc['varName']])

testTargetsLabelEncoder = preprocessing.LabelEncoder()
for colDesc in datasetSchema['trainData']['trainTargets']:
    if colDesc['varType']=='categorical':
        testTargetsLabelEncoder = testTargetsLabelEncoder.fit(testTargets[colDesc['varName']])
        testTargets = testTargetsLabelEncoder.transform(testTargets[colDesc['varName']])
    if colDesc['varRole']=='target':
        break


testData = testData.astype(float)
testTargets = testTargets.astype(float)
testMetadata = MetaFeatures().produce(inputs=[2, testData.to_dict(orient="list"), testTargets])
print(testMetadata)

