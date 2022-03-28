from pickle import FALSE
from turtle import pos
from typing import Dict, Tuple

import numpy as np
import pandas as pd
import string
import joblib
from tqdm import tqdm
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction import text
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

TRUE_PAIR = 1
FALSE_PAIR = 0

class Dataset:
    def __init__(self) -> None:
        self.x = []
        self.y = []
    
    def addPair(self, a, b, intLabel: int) -> None:
        pair = np.concatenate((a, b), axis=None)
        reversePair = np.concatenate((a, b), axis=None)
        label = float(intLabel)

        # https://stackoverflow.com/questions/14446128/python-append-vs-extend-efficiency
        self.x.extend((pair, reversePair))
        self.y.extend((label, label))


print("Importing data.")
X_filepath = "../X1.csv"
Y_filepath = "../Y1.csv"
X = pd.read_csv(X_filepath)
Y = pd.read_csv(Y_filepath)
X_fixed = X.drop(columns=['id'])
X_fixed.fillna(" ", inplace=True)
X_sum = [' '.join([j[:100] for j in X_fixed.iloc[i]]) for i in range(X_fixed.shape[0])]
X_sum = [i.translate(str.maketrans('', '', string.punctuation)) for i in X_sum]
print(X_sum[0])

print("Vectorize data.")
vectorizer = text.TfidfVectorizer(max_df=0.9, stop_words=text.ENGLISH_STOP_WORDS)
X_tfidf = vectorizer.fit_transform(X_sum).toarray()
print(X_tfidf[0].shape)

print("Create pair values.")
IDsDict = {}
for index, i in X.iterrows():
    IDsDict[i["id"]] = index

trainDataset = Dataset()

possiblePairs: Dict[Tuple[int, int], int] = {}

for i in range(X.shape[0]):
    for j in range(i + 1, X.shape[0]):
        possiblePairs[(i, j)] = FALSE_PAIR

# Y does not have all the possible pairs, only the *true pairs*
for index, i in tqdm(Y.iterrows()):
    left = i["lid"]
    right = i["rid"]
    
    #leftItem = X_tfidf[IDsDict[left]]
    #rightItem = X_tfidf[IDsDict[right]]
    possiblePairs[(IDsDict[left], IDsDict[right])] = TRUE_PAIR
    
while len(possiblePairs) > 0:
    pair, label = possiblePairs.popitem()
    trainDataset.addPair(X_tfidf[pair[0]], X_tfidf[pair[1]], label)

# X_pairs = possiblePairs.keys()
# y = possiblePairs.values()
X_pairs = trainDataset.x
y = trainDataset.y

print("Separate into train and test data.")
X_train, X_test, y_train, y_test = train_test_split(X_pairs, y, test_size=0.1, random_state=42)

exit()

print("Train classifier.")
classifier = RandomForestClassifier(verbose=2, class_weight={0.0:0.01, 1.0:100.0},
    n_jobs=-1, random_state=42)
classifier.fit(X_train, y_train) 

print("Make prediction.")
y_pred = classifier.predict(X_test)
print(confusion_matrix(y_test,y_pred))
print(classification_report(y_test,y_pred))
print(accuracy_score(y_test, y_pred))

print("Save classifier")
joblib.dump(classifier, "./classifier.txt", compress=3)

print("Create final pairs.")
X_pairs_final = []
for i in range(len(X_sum) - 1):
    for j in range(i+1, len(X_sum)):
        leftItem = X_tfidf[i]
        rightItem = X_tfidf[j]
        newItem = np.concatenate((leftItem, rightItem), axis=None)
        X_pairs_final.append(newItem)

print("Run classifier.")
classifier = joblib.load("./classifier.txt")
y_pred = classifier.predict(X_pairs_final)
print(len(y_pred))

print("Save results.")
results = []
y_ind = 0
for i in range(len(X_sum) - 1):
    for j in range(i+1, len(X_sum)):
        newItem = {
            "left_instance_id": X.iloc[i]["instance_id"],
            "right_instance_id": X.iloc[j]["instance_id"],
            "label": int(y_pred[y_ind])
        }
        results.append(newItem)
        y_ind += 1

print(int(np.sum(y_pred)))
results = pd.DataFrame(results)
results.to_csv('./output.csv', index=False)
