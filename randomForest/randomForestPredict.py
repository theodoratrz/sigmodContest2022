import math
from typing import Dict, Tuple

import string
import joblib

import numpy as np 
import pandas as pd
from sklearn.feature_extraction import text
from sklearn.feature_extraction.text import TfidfVectorizer

from utils import TRUE_PAIR

print("Importing data.")
X = pd.read_csv("../datasets/X1.csv")
X_fixed = X.drop(columns=["id"])
X_fixed.fillna(" ", inplace=True)
X_sum = [' '.join([j[:100] for j in X_fixed.iloc[i]]) for i in range(X_fixed.shape[0])]
X_sum = [i.translate(str.maketrans('', '', string.punctuation)) for i in X_sum]

print("Vectorize data.")
vectorizer = TfidfVectorizer(max_df=0.9, stop_words=text.ENGLISH_STOP_WORDS)
X_tfidf = vectorizer.fit_transform(X_sum).toarray()
tfidfVectorSize = X_tfidf[0].shape

print("Run classifier.")
classifier = joblib.load("./classifier.txt")

results = []

# We predict in batches in order to save memory
batchMaxSize = 50
batches = math.ceil(len(X_tfidf) / batchMaxSize)

for b in range(batches):
    limit = min((b+1)*batchMaxSize, len(X_tfidf))
    #batchSize = limit - b*batchMaxSize
    batchPairs = []
    for i in range(b*batchMaxSize, limit - 1):
        for j in range(i+1, len(X_tfidf)):
            leftItem = X_tfidf[i]
            rightItem = X_tfidf[j]
            newItem = np.concatenate((leftItem, rightItem), axis=None)
            batchPairs.append(newItem)
    
    batchPredictions = classifier.predict(batchPairs)
    predIndex = 0
    for i in range(b*batchMaxSize, limit - 1):
        for j in range(i+1, len(X_tfidf)):
            if batchPredictions[predIndex] == TRUE_PAIR:
                newItem = {
                    "left_instance_id": X.iloc[i]["id"],
                    "right_instance_id": X.iloc[j]["id"],
                }
                results.append(newItem)
            predIndex += 1
    
    print(f"Batch {b} done.")

results = pd.DataFrame(results)
results.to_csv('output.csv', index=False)
