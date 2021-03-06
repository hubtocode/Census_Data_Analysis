# -*- coding: utf-8 -*-
"""Team2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1U7NKySwQN20W9kUg1nCmBidpiCiDHHA-

#Classifying if income is >$50k/year from Census Data
###By Team 2

## Plan of action
1. Import dataset
2. High level overview of data such as correlation, skewness etc
3. Data Cleaning & Preprocessing
    - Cleaning columns with "?" on Workclass,  Martial Status and Country
    - Normalizing data values  
    - One Hot Encoding
    - Understanding and removing outliers
4. Modeling
    - Preparing training and target dataset
    - Prediction using LogisticRegression
    - Prediction using RandomForestClassifier
    - Prediction using MLPClassifier
    - Prediction using GaussianNB
    - Prediction using DecisionTreeClassifier
    - Prediction using XGB Boost
    - Prediction using SVM
    - Accuracy based on AUC
5. Predict on Test Dataset

##Short Summary

GaussianNB, Decision Tree classifer and SVC are not being used because the baseline AUC score is marginally lower than other models.

Although XGBoost gave higher AUC score in Train (92.3%), it performed lower on Test set (83%). Therefore we did not choose XGB boost as final model because it was overfitting.

MLP Classifier provided a better AUC score on Train as well as Test hence approprite to deliver results. 

Final AUC Score = 0.893479
"""

#Importing all the libraries
import pandas as pd
import seaborn as sns
import numpy as np
from sklearn import preprocessing
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn import model_selection
from sklearn.metrics import accuracy_score
from sklearn.metrics import roc_auc_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
import matplotlib.pyplot as plt
from sklearn import model_selection
from sklearn.metrics import accuracy_score
from scipy.stats import zscore
from collections import Counter
from sklearn.datasets import make_classification
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
import xgboost as xgb
from imblearn.over_sampling import SMOTE

##Importing data, removing nulls, and one hot encoding values
dataset=pd.read_csv("training.csv")
dataset = dataset[(dataset != '?').all(axis=1)]
dataset.drop(columns=['Education'],inplace=True)
dataset['income']=dataset['Over-50K'].map({'<=50K': 0, '>50K': 1})
dataset['Marital_new']=dataset['Marital-Status'].map({'Married-civ-spouse':'Married', 'Divorced':'Single', 'Never-married':'Single', 'Separated':'Single', 
'Widowed':'Single', 'Married-spouse-absent':'Married', 'Married-AF-spouse':'Married'})

## Encoding the categorical variables
for column in dataset:
    enc=preprocessing.LabelEncoder()
    if dataset.dtypes[column]==np.object:
         dataset[column]=enc.fit_transform(dataset[column])
dataset.drop(columns=['Marital_new'],inplace=True)
dataset.drop(columns=['Over-50K'],inplace=True)

## Ploting heatmap to find correlation
plt.figure(figsize=(14,10))
sns.heatmap(dataset.corr(),annot=True,fmt='.2f')
plt.show()

## Preparing dataset for test and train split up

df = dataset[['Age', 'Workclass', 'fnlwgt', 'Education-Num', 'Occupation', 'Relationship', 'Race', 'Sex',
       'Capital-Gain', 'Capital-Loss', 'Hours-per-week', 'Country']].apply(zscore)
df['income'] = dataset['income']
df['income'] = dataset['income']
X= df.drop('income',axis=1)
y= df['income']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20,random_state=5)

smt = SMOTE()
X_train, y_train = smt.fit_sample(X_train, y_train)
X_train = pd.DataFrame(X_train,columns = ['Age', 'Workclass', 'fnlwgt', 'Education-Num', 'Occupation', 'Relationship', 'Race', 'Sex',
       'Capital-Gain', 'Capital-Loss', 'Hours-per-week', 'Country'])
y_train = pd.Series(y_train)

## Creating multiple models as list and then evaluating each model's accuracy

models = []
names = ['LR','Random Forest','Neural Network','GaussianNB','DecisionTreeClassifier','SVM',]

models.append((LogisticRegression()))
models.append((RandomForestClassifier(n_estimators=100)))
models.append((MLPClassifier()))
models.append((GaussianNB()))
models.append((DecisionTreeClassifier()))
models.append((SVC()))

#Print AUC scores for each model

kfold = model_selection.KFold(n_splits=5,random_state=42)

for i in range(0,len(models)):    
    cv_result = model_selection.cross_val_score(models[i],X_train,y_train,cv=kfold,scoring='accuracy')
    score=models[i].fit(X_train,y_train)
    prediction = models[i].predict(X_test)
    acc_score = accuracy_score(y_test,prediction)     
    print ('-'*40)
    print ('{0}: {1}'.format(names[i],acc_score))

eval_set=[(X_train,y_train),(X_test,y_test)]
classifier= xgb.XGBClassifier(learning_rate=0.01,n_estimators=1500,max_depth=7,min_child_weight=1,gamma=0,
                                 subsample=0.8,colsample_bytree=0.9,nthread=4,scale_pos_weight=1,seed=27)
classifier.fit(X_train, y_train ,eval_metric=['auc'], eval_set=eval_set)

## XGB boost model AUC Score on Train
y_pred = classifier.predict_proba(X_test)
pred=[]
for i in range(len(y_pred)):
    pred.append(y_pred[i][1])
auc = roc_auc_score(y_test, pred)
print("AUC Score:", auc)

y_pred = classifier.predict(X_test)

print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

print("Classification Report")
print(classification_report(y_test, y_pred))

#Importing test csv file provided, removing nulls and handling other columns
test=pd.read_csv("test.csv")
test = test[(test != '?').all(axis=1)]
test.drop(columns=['Education'],inplace=True)
test['income']=test['Over-50K'].map({'<=50K': 0, '>50K': 1})
test['Marital_new']=test['Marital-Status'].map({'Married-civ-spouse':'Married', 'Divorced':'Single', 'Never-married':'Single', 'Separated':'Single', 
'Widowed':'Single', 'Married-spouse-absent':'Married', 'Married-AF-spouse':'Married'})

for column in test:
    enc=preprocessing.LabelEncoder()
    if test.dtypes[column]==np.object:
         test[column]=enc.fit_transform(test[column])
test.drop(columns=['Marital_new'],inplace=True)
test.drop(columns=['Over-50K'],inplace=True)

## APplying z-score on test data set
from scipy.stats import zscore
df_test = test[['Age', 'Workclass', 'fnlwgt', 'Education-Num', 'Occupation', 'Relationship', 'Race', 'Sex',
       'Capital-Gain', 'Capital-Loss', 'Hours-per-week', 'Country']].apply(zscore)
df_test['income'] = test['income']
df_test_x= df_test[['Age', 'Workclass', 'fnlwgt', 'Education-Num', 'Occupation', 'Relationship', 'Race', 'Sex',
       'Capital-Gain', 'Capital-Loss', 'Hours-per-week', 'Country']]
df_test_y = df_test[['income']]

##XGB Boost Classifier
y_pred = classifier.predict_proba(df_test_x)
pred=[]
for i in range(len(y_pred)):
    pred.append(y_pred[i][1])
auc = roc_auc_score(df_test_y, pred)
print("AUC Score:", auc)

y_pred = classifier.predict(df_test_x)

print("Confusion Matrix:")
print(confusion_matrix(df_test_y, y_pred))

print("Classification Report")
print(classification_report(df_test_y, y_pred))

##Random Forest Classifier
y_pred = models[1].predict_proba(df_test_x)
pred=[]
for i in range(len(y_pred)):
    pred.append(y_pred[i][1])
auc = roc_auc_score(df_test_y, pred)
print("AUC Score:", auc)

y_pred = models[1].predict(df_test_x)

print("Confusion Matrix:")
print(confusion_matrix(df_test_y, y_pred))

print("Classification Report")
print(classification_report(df_test_y, y_pred))

##MLP Classifier
y_pred = models[2].predict_proba(df_test_x)
pred=[]
for i in range(len(y_pred)):
    pred.append(y_pred[i][1])
auc = roc_auc_score(df_test_y, pred)
print("AUC Score:", auc)

y_pred = models[2].predict(df_test_x)

print("Confusion Matrix:")
print(confusion_matrix(df_test_y, y_pred))

print("Classification Report")
print(classification_report(df_test_y, y_pred))