import math
from typing import Dict, Tuple

import string
import joblib
import kmeans

import numpy as np 
import pandas as pd
from sklearn.feature_extraction import text
from sklearn.feature_extraction.text import TfidfVectorizer


from utils import TRUE_PAIR

X_filepath = "X1.csv"
X = pd.read_csv(X_filepath)

print("Run classifier.")
classifier = joblib.load("./classifier.txt")

points , indices = kmeans.cluster()
results = []

for index, cluster in points.items() :

    for i in range(len(cluster)):
        for j in range(i+1, len(cluster)):
            leftItem = cluster[i]
            rightItem = cluster[j]
            newItem = np.concatenate((leftItem, rightItem), axis=None)
            clusterPredictions = classifier.predict([newItem])
            if clusterPredictions == TRUE_PAIR:
                newItem = {
                    "left_instance_id": X.iloc[indices[index][i]]["id"],
                    "right_instance_id": X.iloc[indices[index][j]]["id"],
                }
                results.append(newItem)
            del(clusterPredictions) 
    print(f"Cluster {index} done.")

results = pd.DataFrame(results)
results.to_csv('output.csv', index=False)
