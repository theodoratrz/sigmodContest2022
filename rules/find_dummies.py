from dummy_utils import looksSimilar, cleanInstance

import numpy as np
import pandas as pd

X = pd.read_csv("../datasets/X1.csv")
X_clean = np.empty(shape=X.shape[0], dtype=object)

for i, row in X.iterrows():
    X_clean[i] = (row['title'], cleanInstance(row['title']))

dummyPairs = []

for i in range(len(X_clean)):
    for j in range(i + 1, len(X_clean)):
        a, (a_clean_words, a_clean) = X_clean[i]
        b, (b_clean_words, b_clean) = X_clean[j]
        
        if (a_clean == b_clean) or looksSimilar(a_clean_words, b_clean_words):
            dummyPairs.append({
                "left_instance": a,
                "right_instance": b
            })

out = pd.DataFrame(dummyPairs)
out.to_csv("./dummy_output.csv", index=False)
