from typing import List, Dict
import string

import pandas as pd

THRESHOLD = 11
def looksSimilar(words1: List[str], words2: List[str]):
    count = 0
    for w1, w2 in zip(words1, words2):
        if w1 == w2:
            count += 1
            if count == THRESHOLD:
                return True
    return False

def cleanInstance(raw: str):
    raw_low = raw.lower()
    no_punct = raw_low.translate(str.maketrans({ord(c): ' ' for c in string.punctuation}))
    words = no_punct.split()
    words.sort()

    return words, ' '.join(words)

def addPair(a: str, b: str, pairs: List[Dict[str, str]]):
    pairs.append({
        "left_instance": a,
        "right_instance": b
    })

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
        addPair(a, b, dummyPairs)

out = pd.DataFrame(dummyPairs)
out.to_csv("./dummies_real.csv", index=False)
