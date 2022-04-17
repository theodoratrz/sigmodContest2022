import pandas as pd

from dummy_utils import looksSimilar, cleanInstance

Y = pd.read_csv("../datasets/Y1.csv")
X = pd.read_csv("../datasets/X1.csv")

idToTitle = {}
dummyPairs = []

for index, row in X.iterrows():
    idToTitle[row['id']] = row['title']

for index, row in Y.iterrows():
    a = idToTitle[row['lid']]
    b = idToTitle[row['rid']]

    a_clean_words, a_clean = cleanInstance(a)
    b_clean_words, b_clean = cleanInstance(b)
    
    if (a_clean == b_clean) or looksSimilar(a_clean_words, b_clean_words):
        dummyPairs.append({
        "left_instance": a,
        "right_instance": b
    })

out = pd.DataFrame(dummyPairs)
out.to_csv("./dummies_real.csv", index=False)
