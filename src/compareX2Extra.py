import csv
from typing import List, Dict, Tuple

titleToCell: Dict[str, Tuple[int, int]] = {
    "id1": (0, 0),
    "title1": (0, 1),
    "price1": (0, 2),
    "brand1": (0, 3),
    "description1": (0, 4),
    "category1": (0, 5),
    "id2": (1, 0),
    "title2": (1, 1),
    "price2": (1, 2),
    "brand2": (1, 3),
    "description2": (0, 4),
    "category2": (0, 5),
}

with open('output.csv') as outFile:
    outRows = [[r[0], r[1]] for r in csv.reader(outFile)][1:]
with open("../datasets/Y2.csv") as trueFile:
    trueRows = [r for r in csv.reader(trueFile)][1:]

duplicates = [r for r in outRows if [r[1], [0]] in outRows]

common = [r for r in trueRows if r in outRows]

missed = [r for r in trueRows if r not in outRows]

falsePositives = [r for r in outRows if r not in trueRows]

with open("../datasets/X2.csv") as instancesFile:
    instancesRows = [r for r in csv.reader(instancesFile)][1:]

instances: Dict[str, List[str]] = {}
for row in instancesRows:
    instances[row[0]] = row

def pairToRowDict(pair: List[str]):
    return {title: instances[pair[i]][j] for title, (i, j) in titleToCell.items()}

fileRows: List[Tuple[ str, List[List[str]] ]] = [
    ("true.csv", trueRows),
    ("../output/common.csv", common),
    ("missed.csv", missed),
    ("false.csv", falsePositives)
]

for filename, rows in fileRows:
    with open(filename, mode="w") as outCsv:
        writer = csv.DictWriter(outCsv, fieldnames=titleToCell.keys())
        writer.writeheader()
        writer.writerows([pairToRowDict(p) for p in rows])

print(f"Common: {len(common)}")
print(f"Missed: {len(missed)}")
print(f"False Positives: {len(falsePositives)}")
print(f"Recall: {(len(common)/len(trueRows)):.3}")
print(f'Duplicates: {len(duplicates)}')
