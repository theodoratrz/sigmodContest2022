from typing import Dict, Tuple
import random
import string
import joblib

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction import text
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

from utils import Dataset, TRUE_PAIR, FALSE_PAIR

random.seed(42)

print("Importing data.")
X_filepath = "X1.csv"
Y_filepath = "Y1.csv"
X = pd.read_csv(X_filepath)
Y = pd.read_csv(Y_filepath)
X_fixed = X.drop(columns=['id'])
X_fixed.fillna(" ", inplace=True)
X_sum = [' '.join([j[:100] for j in X_fixed.iloc[i]]) for i in range(X_fixed.shape[0])]
X_sum = [i.translate(str.maketrans('', '', string.punctuation)) for i in X_sum]

print("Vectorize data.")
vectorizer = text.TfidfVectorizer(max_df=0.9, stop_words=text.ENGLISH_STOP_WORDS)
X_tfidf = vectorizer.fit_transform(X_sum).toarray()
print(X_tfidf[0].shape)

print("Create pair values.")
idsToIndexes = {}
for index, i in X.iterrows():
    idsToIndexes[i["id"]] = index

trainDataset = Dataset()

possiblePairs: Dict[Tuple[int, int], float] = {}

# Y does not have all the possible pairs, only the *true pairs*
for index, i in Y.iterrows():
    left = idsToIndexes[i["lid"]]
    right = idsToIndexes[i["rid"]]
    
    possiblePairs[(left, right)] = TRUE_PAIR

numTruePairs = len(possiblePairs)
while len(possiblePairs) < 2*numTruePairs:
    i = random.randint(0, X.shape[0] - 2)
    j = random.randint(i + 1, X.shape[0] - 1)

    if (i, j) not in possiblePairs:
        possiblePairs[(i, j)] = FALSE_PAIR

while len(possiblePairs) > 0:
    pair, label = possiblePairs.popitem()
    trainDataset.addPair(X_tfidf[pair[0]], X_tfidf[pair[1]], label)

X_pairs = trainDataset.x
y = trainDataset.y

print("Separate into train and test data.")
X_train, X_test, y_train, y_test = train_test_split(X_pairs, y, test_size=0.1, random_state=42)

print("Train classifier.")
classifier = RandomForestClassifier(verbose=0, class_weight={FALSE_PAIR:0.01, TRUE_PAIR:100.0},
                                    n_jobs=-1, random_state=42)
classifier.fit(X_train, y_train) 

print("Save classifier")
joblib.dump(classifier, "./classifier.txt", compress=3)
