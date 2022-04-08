import pandas as pd
import re

Flag = True

if __name__ == '__main__':
    file_name = 'Y1.csv'
    data = pd.read_csv(file_name)
    ids = data.to_dict('list')
    
    file_name2 = '/home/theodora/Documents/SigmodContest/sigmodContest2022/rules/output.csv'
    data2 = pd.read_csv(file_name2)
    id2 = data2.to_dict('list')
    
    counter = 0
    couples = []
    couplesToTest = []
    couplesNotFound = []
    Allcouples = []
    rightCouples = []

    for index in range(len(ids['lid'])):
        y = (ids['lid'][index], ids['rid'][index])
        couples.append(y)

    for index in range(len(id2['lid'])):
        y = (id2['lid'][index], id2['rid'][index])
        Allcouples.append(y)

    for index in range(len(id2['lid'])):
        t = (id2['lid'][index], id2['rid'][index])
        if t in couples:
            rightCouples.append(t)
            counter+=1
        else:
            couplesToTest.append(t)
    
    for index in range(len(couples)):
        u = couples[index]
        if u not in Allcouples:
            couplesNotFound.append(u)

    print(counter*100/2815)
    print(counter)
    couplesNotFound = pd.DataFrame(couplesNotFound)
    name = [
        'lid',
        'rid'
    ]
    for i in range(len(name)):
        couplesNotFound.rename({i: name[i]}, inplace=True, axis=1)

    couplesNotFound.to_csv("couples_to_test.csv", sep=',', encoding='utf-8', index=False)
    
