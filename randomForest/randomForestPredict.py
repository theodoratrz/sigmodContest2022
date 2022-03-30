import gc

import string
import joblib

import pandas as pd
from sklearn.feature_extraction import text
from sklearn.feature_extraction.text import TfidfVectorizer

from utils import Batch

def predict(batchMaxSize: int, verbose: bool = False):

    print("Importing data.")
    X = pd.read_csv("./X1.csv")
    X_fixed = X.drop(columns=["id"])
    X_fixed.fillna(" ", inplace=True)
    X_sum = [' '.join([j[:100] for j in X_fixed.iloc[i]]) for i in range(X_fixed.shape[0])]
    X_sum = [i.translate(str.maketrans('', '', string.punctuation)) for i in X_sum]

    print("Vectorize data.")
    vectorizer = TfidfVectorizer(max_df=0.9, stop_words=text.ENGLISH_STOP_WORDS)
    X_tfidf = vectorizer.fit_transform(X_sum).toarray()

    del X_fixed
    del X_sum
    gc.collect()

    print("Run classifier.")
    classifier = joblib.load("./classifier.txt")
    classifier.verbose = 0

    results = []

    # We predict in batches in order to save memory
    batch = Batch(batchMaxSize)
    batchesCompleted = 0
    for i in range(len(X_tfidf)):
        i_id = X.iloc[i]["id"]
        for j in range(i+1, len(X_tfidf)):
            if batch.isFull():
                batch.makePredictions(classifier)
                batch.storePredictions(results)
                batch.reset()
                batchesCompleted += 1
                if verbose:
                    print(f"{batchesCompleted:3} batches done.\r", end="")
                if len(results) == 1000000:
                    return results
            
            leftItem = X_tfidf[i]
            rightItem = X_tfidf[j]
            batch.addPair(leftItem, rightItem, i_id, X.iloc[j]["id"])

    del X

    if batch.isNotEmpty():
        batch.makePredictions(classifier)
        batch.storePredictions(results)
        batch.reset(triggerGC=True)
        if verbose:
            print(f"{batchesCompleted:3} batches done.")
    
    return results
