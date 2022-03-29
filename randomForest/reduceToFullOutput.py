import numpy as np 
import pandas as pd
import string 
from tqdm import tqdm
from sklearn.metrics import confusion_matrix


print("Import datasets.")
X_filepath = "../datasets/Notebook/X2.csv"
Y_filepath = "../datasets/Notebook/Y2.csv"
X = pd.read_csv(X_filepath)
Y = pd.read_csv(Y_filepath)
X_fixed = X.drop(columns=['instance_id'])
X_fixed.fillna(" ", inplace=True)
X_sum = [' '.join([j[:124] for j in X_fixed.iloc[i]]) for i in range(X_fixed.shape[0])]
X_sum = [i.translate(str.maketrans('', '', string.punctuation)) for i in X_sum]
print(X_sum[0])

print("Import output.")
output_filepath = "output.csv"
output = pd.read_csv(output_filepath)

y_true = []
y_pred = []
for index in tqdm(range(Y.shape[0])):
    leftID = Y.iloc[index]['lid']
    rightID = Y.iloc[index]['rid']
    label = Y.iloc[index]['label']
    y_true.append(int(label))

    reducedLabel = output[
        ((output['left_instance_id'] == leftID) &
        (output['right_instance_id'] == rightID)) |
        ((output['left_instance_id'] == rightID) &
        (output['right_instance_id'] == leftID))
        ]
    
    if reducedLabel.shape[0] == 0:
        y_pred.append(0)
    else:
        y_pred.append(1)

print(sum(y_true))
print(sum(y_pred))

confusion = confusion_matrix(y_true, y_pred, labels=[0, 1])
confusion = pd.DataFrame(confusion, index=[0,1], columns=[0,1])
print("Confusion:")
print(confusion)

