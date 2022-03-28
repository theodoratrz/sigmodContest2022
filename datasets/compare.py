import pandas as pd
import re

Flag = True

if __name__ == '__main__':
    file_name = 'Y1.csv'
    data = pd.read_csv(file_name)
    ids = data.to_dict('list')
    
    file_name2 = 'output.csv'
    data2 = pd.read_csv(file_name2)
    id2 = data2.to_dict('list')
    
    counter = 0
    couples = []
    couplesToTest = []

    for index in range(len(ids['lid'])):
        y = (ids['lid'][index], ids['rid'][index])
        couples.append(y)

    for index in range(len(id2['lid'])):
        t = (id2['lid'][index], id2['rid'][index])
        if t in couples:
            counter+=1
        else:
            couplesToTest.append(t)

    print(counter*100/2815)
    couplesToTest = pd.DataFrame(couplesToTest)
    name = [
        'lid',
        'rid'
    ]
    for i in range(len(name)):
        couplesToTest.rename({i: name[i]}, inplace=True, axis=1)

    couplesToTest.to_csv("couples_to_test.csv", sep=',', encoding='utf-8', index=False)
    
