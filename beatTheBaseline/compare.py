import csv

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

    instances = {}
    for row in instancesRows:
        instances[row[0]] = row[1]

missedTitles = [(instances[r[0]], instances[r[1]]) for r in missed]
falseTitles = [(instances[r[0]], instances[r[1]]) for r in falsePositives]

with open("missed.csv", mode="w") as missedCsv:
    writer = csv.writer(missedCsv)

    writer.writerows(missedTitles)

with open("false.csv", mode="w") as falseCsv:
    writer = csv.writer(falseCsv)

    writer.writerows(falseTitles)
pass

print(f"Common: {len(common)}")
print(f"Missed: {len(missed)}")
print(f"False Positives: {len(falsePositives)}")
print(f"Recall: {(len(common)/len(trueRows)):.3}")
print(f'Duplicates: {len(duplicates)}')
