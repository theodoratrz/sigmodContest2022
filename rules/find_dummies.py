from dummy_utils import looksSimilar, cleanInstance

import numpy as np
import pandas as pd

SUBMISSION_MODE = True

def saveAndExit(dummyPairs):
    if SUBMISSION_MODE:
        dummyPairs.extend([(0,0)]*2000000)
        file = "output.csv"
    else:
        dummyPairs.extend([(0,0)]*2)
        file = "dummy_output.csv"
    
    out = pd.DataFrame(
                dummyPairs,
                columns=[
                    'left_instance_id',
                    'right_instance_id'])

    out.to_csv(file, index=False)

if __name__ == '__main__':
    pd.read_csv("X2.csv")
    X = pd.read_csv("X1.csv")
    X_clean = np.empty(shape=X.shape[0], dtype=object)

    for i, row in X.iterrows():
        X_clean[i] = (row['id'], row['title'], cleanInstance(row['title']))

    dummyPairs = []

    for i in range(len(X_clean)):
        for j in range(i + 1, len(X_clean)):
            a_id, a, (a_clean_words, a_clean) = X_clean[i]
            b_id, b, (b_clean_words, b_clean) = X_clean[j]
            
            if (a_clean == b_clean) or looksSimilar(a_clean_words, b_clean_words):
                if a_id < b_id:
                    dummyPairs.append((a_id, b_id))
                    if len(dummyPairs) == 1000000:
                        saveAndExit(dummyPairs)
                else:
                    dummyPairs.append((b_id, a_id))
                    if len(dummyPairs) == 1000000:
                        saveAndExit(dummyPairs)

    saveAndExit(dummyPairs)
