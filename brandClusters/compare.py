import csv

with open('output.csv') as outFile:
    outRows = [r for r in csv.reader(outFile)][1:]

    with open("../datasets/Y1.csv") as trueFile:
        trueRows = [r for r in csv.reader(trueFile)][1:]

        common = [r for r in trueRows if r in outRows]
        missed = [r for r in trueRows if r not in outRows]
        falsePositives = [r for r in outRows if r not in trueRows]
pass

print(f"Common: {len(common)}")
print(f"Missed: {len(missed)}")
print(f"False Positives: {len(falsePositives)}")
print(f"Recall: {(len(common)/len(trueRows)):.3}")
