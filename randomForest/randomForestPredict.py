from typing import Dict, Tuple

import string
import joblib

import numpy as np 
import pandas as pd
from sklearn.feature_extraction import text
from sklearn.feature_extraction.text import TfidfVectorizer

from dataset import Dataset

# print("Importing data.")
X = pd.read_csv("../datasets/Notebook/X2.csv")
X_fixed = X.drop(columns=['instance_id'])
X_fixed.fillna(" ", inplace=True)
X_sum = [' '.join([j[:100] for j in X_fixed.iloc[i]]) for i in range(X_fixed.shape[0])]
X_sum = [i.translate(str.maketrans('', '', string.punctuation)) for i in X_sum]
# print(X_sum[0])

# print("Vectorize data.")
vectorizer = TfidfVectorizer(max_df=0.9, stop_words=text.ENGLISH_STOP_WORDS)
X_tfidf = vectorizer.fit_transform(X_sum).toarray()
# print(X_tfidf[0].shape)

# print("Create final pairs.")
X_pairs_final = []
for i in range(len(X_sum) - 1):
    for j in range(i+1, len(X_sum)):
        leftItem = X_tfidf[i]
        rightItem = X_tfidf[j]
        newItem = np.concatenate((leftItem, rightItem), axis=None)
        X_pairs_final.append(newItem)

# print("Run classifier.")
classifier = joblib.load("./classifier.txt")
y_pred = classifier.predict(X_pairs_final)
# print(len(y_pred))

# print("Save results.")
results = []
y_ind = 0
for i in range(len(X_sum) - 1):
    for j in range(i+1, len(X_sum)):
        if int(y_pred[y_ind]) == 1:
            newItem = {
                "left_instance_id": X.iloc[i]["instance_id"],
                "right_instance_id": X.iloc[j]["instance_id"],
            }
            results.append(newItem)
        y_ind += 1

# print(int(np.sum(y_pred)))
results = pd.DataFrame(results)
results.to_csv('output.csv', index=False)
